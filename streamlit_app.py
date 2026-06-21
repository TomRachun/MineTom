import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta

# ─── CONFIGURATION ────────────────────────────────────────────────
MAX_TPS = 3
TODAY = str(date.today())

st.title("⛏️ Minecraft Server Management Portal")

# Validate that the secrets URL exists
if "public_gsheets_url" not in st.secrets:
    st.error("Missing configuration. Please check your public_gsheets_url in Streamlit Secrets.")
    st.stop()

# Base sheet URL processing
base_url = st.secrets["public_gsheets_url"]
if "/edit" in base_url:
    base_url = base_url.split("/edit")[0]
if not base_url.endswith("/"):
    base_url += "/"

# Helper function to read worksheets directly using Pandas native CSV engine
def get_sheet_data(worksheet_name):
    csv_url = f"{base_url}gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    try:
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"Failed to read tab '{worksheet_name}'. Verify the tab name exists in your Google Sheet exactly as written.")
        st.stop()

# Helper function to write rows back via your Google web app script
def save_sheet_data(df, worksheet_name):
    if "gsheets_write_url" not in st.secrets:
        return
        
    if worksheet_name == "users":
        cols = ["username", "password"]
    elif worksheet_name == "trades":
        cols = ["id", "seller", "item", "enchants", "price", "created_at", "expires_at", "sale_price", "sale_at", "is_auction", "highest_bid", "highest_bidder"]
    elif worksheet_name == "tps":
        cols = ["username", "remaining_tps"]
        if "username_clean" in df.columns:
            df = df.drop(columns=["username_clean"])
            
    df_save = df.reindex(columns=cols).fillna("")
    rows_list = df_save.values.tolist()
    
    payload = {
        "action": "clear_and_save",
        "sheet": worksheet_name,
        "data": rows_list
    }
    
    try:
        requests.post(st.secrets["gsheets_write_url"], json=payload)
    except Exception as e:
        st.error("Write-back connection failed.")

# Helper to convert dynamic input times to timedelta objects
def calculate_delta(amount, unit):
    if unit == "Minutes":
        return timedelta(minutes=amount)
    elif unit == "Hours":
        return timedelta(hours=amount)
    else:
        return timedelta(days=amount)

# Helper to easily show human-readable remaining time
def format_time_remaining(target_iso):
    try:
        delta = datetime.fromisoformat(str(target_iso)) - datetime.now()
        total_seconds = delta.total_seconds()
        if total_seconds <= 0:
            return "Expired"
        if total_seconds < 3600:
            return f"{round(total_seconds / 60, 1)}m remaining"
        elif total_seconds < 86400:
            return f"{round(total_seconds / 3600, 1)}h remaining"
        else:
            return f"{round(total_seconds / 86400, 1)}d remaining"
    except:
        return "Unknown time"

# Helper to pull numeric values from item text strings safely
def extract_numeric_price(price_str):
    try:
        clean_num = int(''.join(filter(str.isdigit, str(price_str))))
        return clean_num
    except:
        return 0

# Helper to compute exact final sales prices strings
def calculate_sale_display(base_val, sale_mode, pct_off):
    if sale_mode == "Make Free":
        return "Free"
    if pct_off == 100:
        return "Free"
    clean_base = extract_numeric_price(base_val)
    final_num = round(clean_base * (1 - pct_off / 100))
    return f"{final_num} Diamonds"

# Initialize dataframes into session state if not already done
if "df_users" not in st.session_state:
    st.session_state.df_users = get_sheet_data("users")
if "df_trades" not in st.session_state:
    st.session_state.df_trades = get_sheet_data("trades")
if "df_tps" not in st.session_state:
    st.session_state.df_tps = get_sheet_data("tps")
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ─── AUTOMATIC TIMER CLEANUP ──────────────────────────────────────
df_trades_current = st.session_state.df_trades
if not df_trades_current.empty and "expires_at" in df_trades_current.columns:
    now_str = datetime.now().isoformat()
    valid_trades = df_trades_current[(df_trades_current["expires_at"].isna()) | (df_trades_current["expires_at"] == "") | (df_trades_current["expires_at"] > now_str)]
    if len(valid_trades) != len(df_trades_current):
        st.session_state.df_trades = valid_trades
        save_sheet_data(valid_trades, "trades")

# ─── SIDEBAR AUTHENTICATION ────────────────────────────────────────
st.sidebar.header("User Authentication")
if st.session_state.current_user is None:
    auth_action = st.sidebar.radio("Choose Action", ["Login", "Register"])
    auth_user = st.sidebar.text_input("Username").strip().lower()
    auth_pass = st.sidebar.text_input("Password", type="password")
    
    if auth_action == "Login":
        if st.sidebar.button("Login"):
            df = st.session_state.df_users
            user_row = df[df['username'].astype(str).str.strip().str.lower() == auth_user]
            if not user_row.empty and str(user_row.iloc[0]['password']).strip() == str(auth_pass).strip():
                st.session_state.current_user = auth_user
                st.sidebar.success(f"Logged in as {auth_user}")
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials.")
    else:
        if st.sidebar.button("Register"):
            df = st.session_state.df_users
            if not auth_user or not auth_pass:
                st.sidebar.error("Fields cannot be empty.")
            elif auth_user in df['username'].astype(str).str.lower().values:
                st.sidebar.error("Username already exists.")
            else:
                new_user = pd.DataFrame([{"username": auth_user, "password": auth_pass}])
                st.session_state.df_users = pd.concat([df, new_user], ignore_index=True)
                save_sheet_data(st.session_state.df_users, "users")
                st.sidebar.success(f"Registered {auth_user}! Please log in.")
                st.rerun()
else:
    st.sidebar.success(f"Logged in as: **{st.session_state.current_user}**")
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

# ─── MAIN TABS INTERFACE ──────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🛒 Trade Store", "📜 Case Records", "⚡ Teleport Tracker"])

# ==========================================
# TAB 1: TRADE STORE
# ==========================================
with tab1:
    st.header("Server Marketplace")
    df_trades = st.session_state.df_trades
    
    if st.session_state.current_user:
        with st.expander("➕ Create Listing (Sale / Sale Delay / Auction)"):
            item = st.text_input("Item Name")
            is_enchantable = st.checkbox("Enchantable?")
            enchants = []
            if is_enchantable:
                text_input = st.text_input("Enchants (comma separated)")
                enchants = [e.strip() for e in text_input.split(",") if e.strip()]
            
            listing_type = st.radio("Listing Format", ["Standard Fix Price", "Auction (Bidding)"])
            
            st.markdown("##### Duration Settings")
            col_dur, col_unit = st.columns([2, 2])
            with col_dur:
                duration_amount = st.number_input("Time Amount", min_value=1, value=2)
            with col_unit:
                duration_unit = st.selectbox("Time Unit", ["Minutes", "Hours", "Days"], index=1)
                
            if listing_type == "Standard Fix Price":
                base_price_val = st.number_input("Base Price (Diamonds)", min_value=1, value=10)
                
                # ADVANCED DELAYED SALE CONFIG
                has_delayed_sale = st.checkbox("Schedule a future discount sale?")
                sale_price_val = ""
                sale_at_val = ""
                if has_delayed_sale:
                    st.markdown("##### Advanced Scheduled Sale")
                    sale_mode = st.radio("Discount Type", ["Percentage Off (1-100%)", "Make Free"], key="sched_mode")
                    
                    discount_pct = 0
                    if sale_mode == "Percentage Off (1-100%)":
                        discount_pct = st.slider("Select Discount %", min_value=1, max_value=100, value=20, key="sched_pct")
                    
                    # Live Preview Output before saving
                    calculated_price = calculate_sale_display(base_price_val, sale_mode, discount_pct)
                    st.info(f"📊 **Sale Preview:** Price will drop from {base_price_val} Diamonds to **{calculated_price}**")
                    
                    col_sdur, col_sunit = st.columns([2, 2])
                    with col_sdur:
                        delay_amount = st.number_input("Delay Time Amount", min_value=1, value=30, key="sched_amt")
                    with col_sunit:
                        delay_unit = st.selectbox("Delay Time Unit", ["Minutes", "Hours", "Days"], key="sched_unit")
                        
                    sale_price_val = calculated_price
                    sale_at_val = (datetime.now() + calculate_delta(delay_amount, delay_unit)).isoformat()
                
                price_string = f"{base_price_val} Diamonds"
                is_auction_val = False
            else:
                base_price_val = st.number_input("Starting Bid Price (Diamonds)", min_value=1, value=5)
                price_string = f"Starting bid: {base_price_val} Diamonds"
                sale_price_val = ""
                sale_at_val = ""
                is_auction_val = True
            
            if st.button("Publish Listing"):
                if item:
                    next_id = int(df_trades["id"].max() + 1) if not df_trades.empty and 'id' in df_trades.columns else 1
                    exp_time = (datetime.now() + calculate_delta(duration_amount, duration_unit)).isoformat()
                    
                    new_trade = pd.DataFrame([{
                        "id": next_id,
                        "seller": st.session_state.current_user,
                        "item": item,
                        "enchants": str(enchants),
                        "price": price_string,
                        "created_at": datetime.now().isoformat(),
                        "expires_at": exp_time,
                        "sale_price": sale_price_val,
                        "sale_at": sale_at_val,
                        "is_auction": is_auction_val,
                        "highest_bid": base_price_val if is_auction_val else "",
                        "highest_bidder": ""
                    }])
                    st.session_state.df_trades = pd.concat([df_trades, new_trade], ignore_index=True)
                    save_sheet_data(st.session_state.df_trades, "trades")
                    st.success("Market listing added successfully!")
                    st.rerun()
                else:
                    st.error("Item name is required.")
                    
    else:
        st.info("Log in to list items on the market.")

    st.subheader("Active Listings")
    if df_trades.empty or 'item' not in df_trades.columns:
        st.write("No items on sale right now.")
    else:
        now_str = datetime.now().isoformat()
        for idx, row in df_trades.iterrows():
            col1, col2 = st.columns([4, 2])
            
            display_price = str(row.get('price', 'Free'))
            has_any_sale_configured = pd.notna(row.get('sale_at')) and row['sale_at'] != ""
            is_currently_discounted = False
            
            if has_any_sale_configured:
                if now_str >= str(row['sale_at']):
                    display_price = f"🔥 SALE: {row['sale_price']} (Was {row['price']})"
                    is_currently_discounted = True
                else:
                    time_info = format_time_remaining(row['sale_at'])
                    display_price += f" (Drops to {row['sale_price']} in {time_info})"

            with col1:
                if str(row.get('is_auction')) == "True" or row.get('is_auction') is True:
                    st.markdown(f"**🏆 [AUCTION] ID {row['id']}: {row['seller']}'s {row['item']}**")
                    st.caption(f"Enchants: {row.get('enchants', 'None')}")
                    if row.get('highest_bidder'):
                        st.markdown(f"Current Bid: **{row['highest_bid']} Diamonds** by `{row['highest_bidder']}`")
                    else:
                        st.markdown(f"Starting Bid: **{row['highest_bid']} Diamonds**")
                else:
                    st.markdown(f"**🛒 ID {row['id']}: {row['seller']} is selling {row['item']}**")
                    st.markdown(f"Price: **{display_price}**")
                    st.caption(f"Enchants: {row.get('enchants', 'None')}")
                
                if pd.notna(row.get('expires_at')) and row['expires_at'] != "":
                    st.caption(f"⏳ Time left: {format_time_remaining(row['expires_at'])}")
            
            with col2:
                is_admin = st.session_state.current_user == "admin"
                is_seller = st.session_state.current_user == row.get('seller', '')
                is_item_auction = str(row.get('is_auction')) == "True" or row.get('is_auction') is True
                
                # --- AUCTION ACTION CONNECTIONS ---
                if is_item_auction and st.session_state.current_user:
                    if st.session_state.current_user != row['seller']:
                        min_bid = int(row['highest_bid']) + 1
                        bid_amount = st.number_input(f"Bid (Min {min_bid})", min_value=min_bid, step=1, key=f"bid_val_{row['id']}")
                        if st.button("🔨 Place Bid", key=f"bid_btn_{row['id']}"):
                            df_trades.at[idx, 'highest_bid'] = bid_amount
                            df_trades.at[idx, 'highest_bidder'] = st.session_state.current_user
                            st.session_state.df_trades = df_trades
                            save_sheet_data(df_trades, "trades")
                            st.success("You are the highest bidder!")
                            st.rerun()
                
                # --- PORTAL TO MODIFY OR REMOVE SALES ---
                if not is_item_auction and (is_seller or is_admin):
                    # Show Remove Sale button if one is configured/active
                    if has_any_sale_configured:
                        if st.button("🏷️ Remove Sale", key=f"rm_sale_{row['id']}", help="Wipes discount settings and restores base cost"):
                            df_trades.at[idx, 'sale_price'] = ""
                            df_trades.at[idx, 'sale_at'] = ""
                            st.session_state.df_trades = df_trades
                            save_sheet_data(df_trades, "trades")
                            st.success("Sale configuration removed!")
                            st.rerun()
                    else:
                        # Advanced Live Instant Sale Form
                        with st.expander("🏷️ Trigger Sale"):
                            inst_mode = st.radio("Discount Type", ["Percentage Off", "Make Free"], key=f"inst_mode_{row['id']}")
                            
                            inst_pct = 0
                            if inst_mode == "Percentage Off":
                                inst_pct = st.slider("Select Cut %", 1, 100, 25, key=f"inst_sld_{row['id']}")
                            
                            # Real-time calculation preview
                            preview_price = calculate_sale_display(row['price'], inst_mode, inst_pct)
                            st.caption(f"Will change price to: **{preview_price}**")
                            
                            if st.button("Apply Sale Now", key=f"inst_btn_{row['id']}"):
                                df_trades.at[idx, 'sale_price'] = preview_price
                                df_trades.at[idx, 'sale_at'] = datetime.now().isoformat()
                                st.session_state.df_trades = df_trades
                                save_sheet_data(df_trades, "trades")
                                st.success("Discount Applied Live!")
                                st.rerun()

                if is_admin or is_seller:
                    if st.button("❌ Remove Listing", key=f"del_trade_{row['id']}"):
                        st.session_state.df_trades = df_trades.drop(idx)
                        save_sheet_data(st.session_state.df_trades, "trades")
                        st.success("Listing removed!")
                        st.rerun()
            st.divider()

# ==========================================
# TAB 2: CASE RECORDS
# ==========================================
with tab2:
    st.header("Punishment Case Management")
    st.info("Note: Case tracking functionality is held in app cache.")

# ==========================================
# TAB 3: TELEPORT TRACKER (ADMIN CONTROLLED)
# ==========================================
with tab3:
    st.header("Daily Teleport (TP) Tracker")
    st.info(f"Today's Date Reference: **{TODAY}**")
    
    df_tps = st.session_state.df_tps
    tp_username = st.text_input("Enter Minecraft Username to track/use", key="tp_user_input").strip().lower()
    
    if tp_username and not df_tps.empty and 'username' in df_tps.columns:
        df_tps['username_clean'] = df_tps['username'].astype(str).str.strip().str.lower()
        user_tp_row = df_tps[df_tps['username_clean'] == tp_username]
        
        if user_tp_row.empty:
            new_tp_user = pd.DataFrame([{"username": tp_username, "remaining_tps": MAX_TPS, "username_clean": tp_username}])
            df_tps = pd.concat([df_tps, new_tp_user], ignore_index=True)
            st.session_state.df_tps = df_tps
            save_sheet_data(df_tps, "tps")
            current_tps = MAX_TPS
        else:
            current_tps = int(user_tp_row.iloc[0]['remaining_tps'])
            
        st.metric(label=f"Remaining TPs for {tp_username}", value=f"{current_tps} / {MAX_TPS}")
        
        if st.session_state.current_user == "admin":
            col_use, col_reset = st.columns(2)
            user_idx = df_tps[df_tps['username_clean'] == tp_username].index[0]
            
            with col_use:
                if st.button("⚡ Use 1 Teleport", key="btn_use_tp"):
                    if current_tps <= 0:
                        st.error(f"💀 {tp_username} has NO TPs left today!")
                    else:
                        df_tps.at[user_idx, 'remaining_tps'] = current_tps - 1
                        st.session_state.df_tps = df_tps
                        save_sheet_data(df_tps, "tps")
                        st.success(f"Teleport tracked for {tp_username}!")
                        st.rerun()
                        
            with col_reset:
                if st.button("🔄 Admin Reset to Full", key="btn_reset_tp"):
                    df_tps.at[user_idx, 'remaining_tps'] = MAX_TPS
                    st.session_state.df_tps = df_tps
                    save_sheet_data(df_tps, "tps")
                    st.success(f"Reset completed for {tp_username}!")
                    st.rerun()
        else:
            st.warning("⚠️ Only the admin account can adjust or log teleport usages.")
