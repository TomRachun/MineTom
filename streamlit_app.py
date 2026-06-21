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
# Clean up expired trades on page load
df_trades_current = st.session_state.df_trades
if not df_trades_current.empty and "expires_at" in df_trades_current.columns:
    now_str = datetime.now().isoformat()
    # Keep rows where expiration is blank OR still in the future
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
            
            # Form setup depending on options chosen
            if listing_type == "Standard Fix Price":
                base_price_val = st.number_input("Base Price (Diamonds)", min_value=1, value=10)
                duration_hours = st.number_input("Listing Duration (Hours until it expires)", min_value=1, value=48)
                
                # Discount system
                has_delayed_sale = st.checkbox("Schedule a future discount sale?")
                sale_price_val = ""
                sale_at_val = ""
                if has_delayed_sale:
                    delay_hours = st.number_input("Hours before discount activates", min_value=1, value=12)
                    discount_pct = st.slider("Discount percentage (%)", min_value=5, max_value=95, value=20)
                    sale_price_val = f"{round(base_price_val * (1 - discount_pct/100))} Diamonds"
                    sale_at_val = (datetime.now() + timedelta(hours=delay_hours)).isoformat()
                
                price_string = f"{base_price_val} Diamonds"
                is_auction_val = False
            else:
                base_price_val = st.number_input("Starting Bid Price (Diamonds)", min_value=1, value=5)
                duration_hours = st.number_input("Auction Duration (Hours)", min_value=1, value=24)
                price_string = f"Starting bid: {base_price_val} Diamonds"
                sale_price_val = ""
                sale_at_val = ""
                is_auction_val = True
            
            if st.button("Publish Listing"):
                if item:
                    next_id = int(df_trades["id"].max() + 1) if not df_trades.empty and 'id' in df_trades.columns else 1
                    exp_time = (datetime.now() + timedelta(hours=duration_hours)).isoformat()
                    
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
            
            # Determine pricing string based on running sales
            display_price = row.get('price', 'Free')
            is_on_sale = False
            if pd.notna(row.get('sale_at')) and row['sale_at'] != "":
                if now_str >= str(row['sale_at']):
                    display_price = f"🔥 SALE: {row['sale_price']} (Was {row['price']})"
                    is_on_sale = True
                else:
                    # Convert timestamp back to read time left for sale activation
                    try:
                        time_left = datetime.fromisoformat(str(row['sale_at'])) - datetime.now()
                        hours_left = round(time_left.total_seconds() / 3600, 1)
                        display_price += f" (Drops to {row['sale_price']} in {hours_left}h)"
                    except:
                        pass

            with col1:
                if str(row.get('is_auction')) == "True" or row.get('is_auction') is True:
                    st.markdown(f"**🏆 [AUCTION] ID {row['id']}: {row['seller']}'s {row['item']}**")
                    st.caption(f"Enchants: {row.get('enchants', 'None')}")
                    if row.get('highest_bidder'):
                        st.markdown(f"Current Bid: **{row['highest_bid']} Diamonds** by `{row['highest_bidder']}`")
                    else:
                        st.markdown(f"Starting Bid: **{row['highest_bid']} Diamonds** (No bids yet)")
                else:
                    st.markdown(f"**🛒 ID {row['id']}: {row['seller']} is selling {row['item']}**")
                    st.markdown(f"Price: **{display_price}**")
                    st.caption(f"Enchants: {row.get('enchants', 'None')}")
                
                # Expiration readout
                if pd.notna(row.get('expires_at')) and row['expires_at'] != "":
                    try:
                        total_left = datetime.fromisoformat(str(row['expires_at'])) - datetime.now()
                        st.caption(f"⏳ Time left: {round(total_left.total_seconds() / 3600, 1)} hours remaining")
                    except:
                        pass
            
            with col2:
                # ─── AUCTION BIDDING INTERFACE ───
                if (str(row.get('is_auction')) == "True" or row.get('is_auction') is True) and st.session_state.current_user:
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
                
                # Delete permissions
                is_admin = st.session_state.current_user == "admin"
                is_seller = st.session_state.current_user == row.get('seller', '')
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
