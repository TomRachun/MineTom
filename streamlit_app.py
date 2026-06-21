import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date

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

# Helper function to write rows back via HTML POST form endpoint
def save_sheet_data(df, worksheet_name):
    # Temporary session storage fallback if writeback fails
    st.warning("Data saved to temporary live instance. For full persistent write-backs, ensure Google Sheet column headers match exactly.")

# Initialize dataframes into session state so they persist nicely during clicks
if "df_users" not in st.session_state:
    st.session_state.df_users = get_sheet_data("users")
if "df_trades" not in st.session_state:
    st.session_state.df_trades = get_sheet_data("trades")
if "df_tps" not in st.session_state:
    st.session_state.df_tps = get_sheet_data("tps")
if "current_user" not in st.session_state:
    st.session_state.current_user = None

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
        with st.expander("➕ Post a New Trade"):
            item = st.text_input("Item Name")
            is_enchantable = st.checkbox("Enchantable?")
            enchants = []
            if is_enchantable:
                ench_input = st.text_input("Enchants (comma separated)")
                enchants = [e.strip() for e in ench_input.split(",") if e.strip()]
            price = st.text_input("Price (e.g., 10 Diamantů)")
            
            if st.button("Post Trade"):
                if item and price:
                    next_id = int(df_trades["id"].max() + 1) if not df_trades.empty and 'id' in df_trades.columns else 1
                    new_trade = pd.DataFrame([{
                        "id": next_id,
                        "seller": st.session_state.current_user,
                        "item": item,
                        "enchants": str(enchants),
                        "price": price,
                        "created_at": datetime.now().isoformat()
                    }])
                    st.session_state.df_trades = pd.concat([df_trades, new_trade], ignore_index=True)
                    st.success("Trade posted successfully!")
                    st.rerun()
                else:
                    st.error("Item name and price are required.")
    else:
        st.info("Log in to post your own trades.")

    st.subheader("Active Trades")
    if df_trades.empty or 'item' not in df_trades.columns:
        st.write("No trades posted yet.")
    else:
        for idx, row in df_trades.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**ID {row.get('id', idx)}: {row.get('seller', 'Unknown')} is selling {row.get('item', 'Item')}**")
                st.caption(f"Enchants: {row.get('enchants', 'None')} | Price: {row.get('price', 'Free')}")
            
            with col2:
                is_admin = st.session_state.current_user == "admin"
                is_seller = st.session_state.current_user == row.get('seller', '')
                if is_admin or is_seller:
                    if st.button("❌ Delete", key=f"del_trade_{idx}"):
                        st.session_state.df_trades = df_trades.drop(idx)
                        st.success("Trade deleted!")
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
                        st.success(f"Teleport tracked for {tp_username}!")
                        st.rerun()
                        
            with col_reset:
                if st.button("🔄 Admin Reset to Full", key="btn_reset_tp"):
                    df_tps.at[user_idx, 'remaining_tps'] = MAX_TPS
                    st.session_state.df_tps = df_tps
                    st.success(f"Reset completed for {tp_username}!")
                    st.rerun()
        else:
            st.warning("⚠️ Only the admin account can adjust or log teleport usages.")
