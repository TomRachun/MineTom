import streamlit as st
import json
import os
from datetime import datetime, date

# ─── CONFIGURATION & FILE PATHS ───────────────────────────────────
SERVER_FILE = "server_data.json"
TPS_FILE = "tps.json"
MAX_TPS = 3
TODAY = str(date.today())

# ─── DATA LOADING & SAVING ────────────────────────────────────────
def load_server_data():
    if os.path.exists(SERVER_FILE):
        with open(SERVER_FILE, "r") as f:
            return json.load(f)
    return {
        "users": {"admin": "admin123"},
        "cases": [],
        "trades": []
    }

def save_server_data(data):
    with open(SERVER_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_tps_data():
    if not os.path.exists(TPS_FILE):
        return {"date": TODAY, "users": {}}
    with open(TPS_FILE, "r") as f:
        data = json.load(f)
    if data["date"] != TODAY:
        data = {"date": TODAY, "users": {}}
    return data

def save_tps_data(data):
    with open(TPS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ─── SESSION STATE INITIALIZATION ──────────────────────────────────
if "server_data" not in st.session_state:
    st.session_state.server_data = load_server_data()

if "tps_data" not in st.session_state:
    st.session_state.tps_data = load_tps_data()

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Shortcut references
server_data = st.session_state.server_data
tps_data = st.session_state.tps_data

# ─── APP HEADER ──────────────────────────────────────────────────
st.title("⛏️ Minecraft Server Management Portal")

# Sidebar Authentication
st.sidebar.header("User Authentication")
if st.session_state.current_user is None:
    auth_action = st.sidebar.radio("Choose Action", ["Login", "Register"])
    
    auth_user = st.sidebar.text_input("Username").strip().lower()
    auth_pass = st.sidebar.text_input("Password", type="password")
    
    if auth_action == "Login":
        if st.sidebar.button("Login"):
            if auth_user in server_data["users"] and server_data["users"][auth_user] == auth_pass:
                st.session_state.current_user = auth_user
                st.sidebar.success(f"Logged in as {auth_user}")
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials.")
    else:
        if st.sidebar.button("Register"):
            if not auth_user or not auth_pass:
                st.sidebar.error("Fields cannot be empty.")
            elif auth_user in server_data["users"]:
                st.sidebar.error("Username already exists.")
            else:
                server_data["users"][auth_user] = auth_pass
                save_server_data(server_data)
                st.sidebar.success(f"Registered {auth_user}! Please log in.")
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
    
    if st.session_state.current_user:
        with st.expander("➕ Post a New Trade"):
            item = st.text_input("Item Name")
            is_enchantable = st.checkbox("Enchantable?")
            enchants = []
            if is_enchantable:
                ench_input = st.text_input("Enchants (comma separated)")
                enchants = [e.strip() for e in ench_input.split(",") if e.strip()]
            price = st.text_input("Price (e.g., 3 diamonds)")
            
            if st.button("Post Trade"):
                if item and price:
                    new_trade = {
                        "id": len(server_data["trades"]) + 1,
                        "seller": st.session_state.current_user,
                        "item": item,
                        "enchants": enchants,
                        "price": price,
                        "created_at": datetime.now().isoformat()
                    }
                    server_data["trades"].append(new_trade)
                    save_server_data(server_data)
                    st.success("Trade posted successfully!")
                    st.rerun()
                else:
                    st.error("Item name and price are required.")
    else:
        st.info("Log in to post your own trades.")

    st.subheader("Active Trades")
    if not server_data["trades"]:
        st.write("No trades posted yet.")
    else:
        for t in server_data["trades"]:
            ench_str = ", ".join(t["enchants"]) if t["enchants"] else "None"
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**ID {t['id']}: {t['seller']} is selling {t['item']}**")
                st.caption(f"Enchants: {ench_str} | Price: {t['price']}")
            
            with col2:
                is_admin = st.session_state.current_user == "admin"
                is_seller = st.session_state.current_user == t["seller"]
                if is_admin or is_seller:
                    if st.button("❌ Delete", key=f"del_trade_{t['id']}"):
                        server_data["trades"].remove(t)
                        save_server_data(server_data)
                        st.success("Trade deleted!")
                        st.rerun()
            st.divider()

# ==========================================
# TAB 2: CASE RECORDS
# ==========================================
with tab2:
    st.header("Punishment Case Management")
    
    if st.session_state.current_user == "admin":
        with st.expander("🛠️ Admin Tools: Add Case"):
            p_name = st.text_input("Player Name")
            offense = st.text_input("Offense / Rule Broken")
            is_pub = st.checkbox("Make Public?", value=True)
            total_days = st.number_input("Punishment Length (Days, 0 = Permanent)", min_value=0, step=1)
            
            if st.button("Add Case"):
                if p_name and offense:
                    new_case = {
                        "id": len(server_data["cases"]) + 1,
                        "player": p_name,
                        "offense": offense,
                        "public": is_pub,
                        "total_days": total_days,
                        "days_served": 0,
                        "created_at": datetime.now().isoformat()
                    }
                    server_data["cases"].append(new_case)
                    save_server_data(server_data)
                    st.success(f"Case #{new_case['id']} added.")
                    st.rerun()
    
    st.subheader("Case Logs")
    now = datetime.now()
    visible_cases = [
        c for c in server_data["cases"] 
        if st.session_state.current_user == "admin" or c["public"]
    ]
    
    if not visible_cases:
        st.write("No tracked cases available to view.")
    else:
        for c in visible_cases:
            created = datetime.fromisoformat(c["created_at"])
            days_passed = (now - created).days
            approx_served = c["days_served"] + days_passed
            
            if c["total_days"] == 0:
                remaining = "Permanent"
            else:
                remaining = max(0, c["total_days"] - approx_served)
            
            status_label = "🟢 Public" if c["public"] else "🔴 Private"
            st.markdown(f"### Case #{c['id']}: {c['player']} ({status_label})")
            st.write(f"**Offense:** {c['offense']}")
            st.write(f"**Total Required Days:** {c['total_days'] if c['total_days'] > 0 else 'Permanent'}")
            st.write(f"**Approx. Days Served:** {approx_served} | **Remaining:** {remaining}")
            
            if st.session_state.current_user == "admin":
                adm_col1, adm_col2 = st.columns(2)
                with adm_col1:
                    new_tot = st.number_input(f"Modify Total Days (Case {c['id']})", min_value=0, value=int(c['total_days']), key=f"tot_{c['id']}")
                    if new_tot != c['total_days']:
                        c['total_days'] = new_tot
                        save_server_data(server_data)
                        st.success("Updated total days!")
                        st.rerun()
                with adm_col2:
                    served_change = st.number_input(f"Add/Sub Served Days (Case {c['id']})", step=1, key=f"srv_{c['id']}")
                    if served_change != 0:
                        c['days_served'] = max(0, c['days_served'] + served_change)
                        save_server_data(server_data)
                        st.success("Updated served adjustments!")
                        st.rerun()
                
                if st.button(f"🗑️ Permanent Delete Case #{c['id']}", key=f"del_case_{c['id']}"):
                    server_data["cases"] = [case for case in server_data["cases"] if case["id"] != c["id"]]
                    save_server_data(server_data)
                    st.success("Case deleted.")
                    st.rerun()
            st.divider()

# ==========================================
# TAB 3: TELEPORT TRACKER (ADMIN CONTROLLED)
# ==========================================
with tab3:
    st.header("Daily Teleport (TP) Tracker")
    st.info(f"Today's Date Reference: **{TODAY}** (Resets daily)")
    
    # Using 'key' binds this input directly to st.session_state.tp_user_input
    tp_username = st.text_input("Enter Minecraft Username to track/use", key="tp_user_input").strip().lower()
    
    if tp_username:
        # Load up-to-date data directly from state reference
        if tp_username not in st.session_state.tps_data["users"]:
            st.session_state.tps_data["users"][tp_username] = MAX_TPS
            save_tps_data(st.session_state.tps_data)
            
        current_tps = st.session_state.tps_data["users"][tp_username]
        st.metric(label=f"Remaining TPs for {tp_username}", value=f"{current_tps} / {MAX_TPS}")
        
        # Only admins can view action buttons and interact
        if st.session_state.current_user == "admin":
            col_use, col_reset = st.columns(2)
            with col_use:
                # Unique key ensures the button state registers perfectly
                if st.button("⚡ Use 1 Teleport", key="btn_use_tp"):
                    if current_tps <= 0:
                        st.error(f"💀 {tp_username} has NO TPs left today!")
                    else:
                        st.session_state.tps_data["users"][tp_username] -= 1
                        save_tps_data(st.session_state.tps_data)
                        st.success(f"Teleport tracked for {tp_username}!")
                        st.rerun()
                        
            with col_reset:
                if st.button("🔄 Admin Reset to Full", key="btn_reset_tp"):
                    st.session_state.tps_data["users"][tp_username] = MAX_TPS
                    save_tps_data(st.session_state.tps_data)
                    st.success(f"Reset completed for {tp_username}!")
                    st.rerun()
        else:
            st.warning("⚠️ Only the admin account can adjust or log teleport usages.")
            # ─── TEMPORARY DEBUG VISUALIZER ──────────────────────────────────
st.divider()
if st.checkbox("⚙️ Show Raw JSON Data (Admin Only)"):
    if st.session_state.current_user == "admin":
        st.subheader("Current Server Data JSON")
        st.json(server_data)
        st.subheader("Current TPs Data JSON")
        st.json(tps_data)
    else:
        st.error("You must be logged in as admin to view raw data.")
