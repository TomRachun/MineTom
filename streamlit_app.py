import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import time

# ─── AUTO-REFRESH CONFIGURATION ──────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# ─── CONFIGURATION & DATA (MAPPED TO: (PRICE, SUGGESTED_AMOUNT)) ───
MAX_TPS = 3
TODAY = str(date.today())

PRICE_SUGGESTIONS = {
    "Custom Item / Jiný předmět": (0, 1),
    "Netherite Ingot": (8, 1),
    "Diamond Block": (9, 1),
    "Elytra": (150, 1),
    "Shulker Box": (20, 1),
    "Beacon": (40, 1),
    "Totem of Undying": (30, 1),
    "Nether Star": (30, 1),
    "Ancient Debris": (2, 1),
    "Mending Book": (50, 1),
    "Silk Touch Book": (30, 1),
    "Unbreaking III Book": (30, 1),
    "Efficiency V Book": (40, 1),
    "Trident": (80, 1),
    "Horse (Tamed / High Stats)": (5, 1),
    "Donkey / Mule": (4, 1),
    "Villager (Unemployed)": (6, 1),
    "Mending Villager": (25, 1),
    "Armorer Villager (Master)": (15, 1),
    "Wolf / Dog": (2, 1),
    "Cat": (2, 1),
    "Axolotl (Blue Rare)": (10, 1),
    "Axolotl (Standard)": (2, 1),
    "Bee Nest (With 3 Bees)": (4, 1),
    "Frog / Toad": (2, 1),
    "Camel": (6, 1),
    "Sniffer Egg": (8, 1),
    "Enchanted Golden Apple": (10, 1),
    "Golden Apple": (1, 1),
    "Block of Netherite": (72, 1),
    "Emerald Block": (2, 1),
    "Gold Block": (3, 1),
    "Iron Block": (1, 1),
    "Sea Lantern (Stack)": (4, 64),
    "Glowstone (Stack)": (2, 64),
    "Rocket's x16": (1, 16),
    "Crying Obsidian (Stack)": (3, 64),
    "Wither Skeleton Skull": (5, 3),
    "Sponge Block": (2, 1),
    "Blaze Rod (Stack)": (3, 64),
    "Ender Pearl (Stack)": (2, 16),
    "Gunpowder (Stack)": (3, 64),
    "Phantom Membrane": (1, 1),
    "Slimeball (Stack)": (2, 64),
    "Dragon's Breath": (2, 1)
}

# ─── TRANSLATION DICTIONARY ──────────────────────────────────────
LOCALES = {
    "English": {
        "title": "⛏️ Minecraft Server Management Portal",
        "auth_header": "User Authentication",
        "choose_action": "Choose Action",
        "username": "Username",
        "password": "Password",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "tabs": ["🛒 Trade Store", "📜 Custom Orders", "⚡ Tracker & Arrests", "🎟️ Sale Codes"],
        "marketplace": "Server Marketplace & Exchange",
        "create_listing": "➕ Create Listing (Sale / Sale Delay / Auction)",
        "item_name": "Item Selection (Type to Search)",
        "custom_item": "Enter Custom Item Name",
        "item_amount": "Amount / Quantity",
        "suggested": "💡 Suggested:",
        "diamonds": "Diamonds",
        "enchantable": "Enchantable?",
        "enchants_placeholder": "Enchants (comma separated)",
        "format": "Listing Format",
        "fixed_price": "Standard Fix Price",
        "auction_format": "Auction (Bidding)",
        "duration_settings": "##### Duration Settings",
        "stay_forever": "Stay Forever (No Expiration Timer)",
        "time_amount": "Time Amount",
        "time_unit": "Time Unit",
        "base_price": "Base Price (Diamonds)",
        "start_bid": "Starting Bid Price (Diamonds)",
        "publish": "Publish Listing",
        "active_listings": "Active Listings",
        "global_coupon_label": "🎟️ Apply Promo / Sale Code for Checkout",
        "global_coupon_placeholder": "Enter code (e.g. VOLBA25) and press Enter",
        "no_items": "No items on sale right now.",
        "forever": "Stay Forever",
        "remove_listing": "❌ Remove Listing",
        "refresh_btn": "🔄 Force Refresh Data",
        "code_header": "🎟️ Promo & Sale Codes Manager",
        "create_code": "➕ Create New Sale Code",
        "code_input": "Sale Code Name (e.g. VOLBA25)",
        "code_pct": "Discount Percentage",
        "code_scope": "Code Target Scope",
        "scope_global": "Global (All your items)",
        "scope_choose_one": "Global (Customer chooses 1 item)",
        "scope_specific": "Specific Listing IDs only",
        "specific_help": "Enter comma separated IDs (e.g. 1, 4, 12)",
        "btn_create_code": "Generate Code",
        "code_success": "✅ Code Applied! Price updated.",
        "code_already_used": "⚠️ You have reached the usage limit for this code!",
        "code_banned_expl": "🚫 Banned Item Names or Listing IDs (Comma Separated)",
        "code_blocked_msg": "🚫 Code blocked! This item or listing ID is blacklisted by the shop owner.",
        "not_owned_err": "⚠️ Security Alert: You cannot blacklist Listing IDs that you do not own!"
    },
    "Čeština": {
        "title": "⛏️ Minecraft Server Portál Správy",
        "auth_header": "Autentizace Uživatele",
        "choose_action": "Vyberte Akci",
        "username": "Uživatelské jméno",
        "password": "Heslo",
        "login": "Přihlásit se",
        "register": "Registrovat",
        "logout": "Odhlásit se",
        "tabs": ["🛒 Obchod / Tržiště", "📜 Zakázky / Objednávky", "⚡ Tracker a Tresty", "🎟️ Slevové Kódy"],
        "marketplace": "Serverové Tržiště a Výměna",
        "create_listing": "➕ Vytvořit Nabídku (Sleva / Zpožděný prodej / Aukce)",
        "item_name": "Výběr Předmětu (Pište pro hledání)",
        "custom_item": "Zadejte vlastní název předmětu",
        "item_amount": "Množství / Počet",
        "suggested": "💡 Doporučeno:",
        "diamonds": "Diamantů",
        "enchantable": "Očarovatelný (Enchanty)?",
        "enchants_placeholder": "Enchanty (oddělené čárkou)",
        "format": "Formát Nabídky",
        "fixed_price": "Standardní Pevná Cena",
        "auction_format": "Aukce (Přihazování)",
        "duration_settings": "##### Nastavení Doby Trvání",
        "stay_forever": "Zůstat navždy (Bez časovače expirace)",
        "time_amount": "Množství času",
        "time_unit": "Časová jednotka",
        "base_price": "Základní Cena (Diamanty)",
        "start_bid": "Vyvolávací Cena (Diamanty)",
        "publish": "Publikovat Nabídku",
        "active_listings": "Aktivní Nabídky",
        "global_coupon_label": "🎟️ Použít slevový / promo kód pro nákup",
        "global_coupon_placeholder": "Zadejte kód (např. VOLBA25) a stiskněte Enter",
        "no_items": "Momentálně nejsou v nabídce žádné položky.",
        "forever": "Navždy",
        "remove_listing": "❌ Odstranit Nabídku",
        "refresh_btn": "🔄 Vynutit Obnovení Dat",
        "code_header": "🎟️ Správce Slevových Kódů",
        "create_code": "➕ Vytvořit Nový Slevový Kód",
        "code_input": "Název kódu (např. VOLBA25)",
        "code_pct": "Výše slevy v procentech",
        "code_scope": "Rozsah Platnosti Kódu",
        "scope_global": "Globální (Všechny moje předměty)",
        "scope_choose_one": "Globální (Zákazník si vybere 1 položku)",
        "scope_specific": "Pouze specifické ID nabídek",
        "specific_help": "Zadejte ID oddělená čárkou (např. 1, 4, 12)",
        "btn_create_code": "Generovat Kód",
        "code_success": "✅ Kód uplatněn! Cena byla upravena.",
        "code_already_used": "⚠️ Dosáhl jsi limitu použití tohoto kódu!",
        "code_banned_expl": "🚫 Zakázané názvy předmětů nebo ID nabídek (oddělené čárkou)",
        "code_blocked_msg": "🚫 Kód zablokován! Tento předmět nebo ID nabídky je majitelem na černé listině.",
        "not_owned_err": "⚠️ Bezpečnostní upozornění: Nemůžete zablokovat ID nabídek, které nevlastníte!"
    }
}

st.sidebar.header("🌐 Language / Jazyk")
lang = st.sidebar.selectbox("Choose Language", ["English", "Čeština"])
T = LOCALES[lang]

st.title(T["title"])

if "public_gsheets_url" not in st.secrets:
    st.error("Missing configuration. Please check your public_gsheets_url in Streamlit Secrets.")
    st.stop()

base_url = st.secrets["public_gsheets_url"]
if "/edit" in base_url:
    base_url = base_url.split("/edit")[0]
if not base_url.endswith("/"):
    base_url += "/"

def get_sheet_data(worksheet_name):
    csv_url = f"{base_url}gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    try:
        return pd.read_csv(csv_url)
    except:
        return pd.DataFrame()

def save_sheet_data(df, worksheet_name):
    if "gsheets_write_url" not in st.secrets:
        return
    if worksheet_name == "users":
        cols = ["username", "password"]
    elif worksheet_name == "trades":
        cols = ["id", "seller", "item", "amount", "enchants", "price", "created_at", "expires_at", "sale_price", "sale_at", "is_auction", "highest_bid", "highest_bidder"]
    elif worksheet_name == "codes":
        cols = ["code", "creator", "discount", "target_ids", "banned_items", "max_uses"]
    elif worksheet_name == "claimed_codes":
        cols = ["username", "code"]
    elif worksheet_name == "tps":
        cols = ["username", "remaining_tps", "jail_reason", "jail_until"]
    elif worksheet_name == "orders":
        cols = ["id", "buyer", "item", "target_qty", "current_qty", "reward_diamonds"]
        
    df_save = df.reindex(columns=cols).fillna("")
    payload = {"action": "clear_and_save", "sheet": worksheet_name, "data": df_save.values.tolist()}
    try: requests.post(st.secrets["gsheets_write_url"], json=payload)
    except: pass

def calculate_delta(amount, unit):
    if unit in ["Minutes", "Minuty"]: return timedelta(minutes=amount)
    elif unit in ["Hours", "Hodiny"]: return timedelta(hours=amount)
    else: return timedelta(days=amount)

def format_time_remaining(target_iso):
    if pd.isna(target_iso) or str(target_iso).strip() in ["", "nan", "Permanent"]: return T["forever"]
    try:
        delta = datetime.fromisoformat(str(target_iso)) - datetime.now()
        total_seconds = delta.total_seconds()
        if total_seconds <= 0: return "Expired"
        if total_seconds < 3600: return f"{round(total_seconds / 60, 1)}m"
        elif total_seconds < 86400: return f"{round(total_seconds / 3600, 1)}h"
        else: return f"{round(total_seconds / 86400, 1)}d"
    except: return T["forever"]

def extract_numeric_price(price_str):
    try: return int(''.join(filter(str.isdigit, str(price_str))))
    except: return 0

# Initialize structures
if "df_users" not in st.session_state: st.session_state.df_users = get_sheet_data("users")
if "df_trades" not in st.session_state: st.session_state.df_trades = get_sheet_data("trades")
if "df_codes" not in st.session_state: st.session_state.df_codes = get_sheet_data("codes")
if "df_claimed" not in st.session_state: st.session_state.df_claimed = get_sheet_data("claimed_codes")
if "df_tps" not in st.session_state: st.session_state.df_tps = get_sheet_data("tps")
if "df_orders" not in st.session_state: st.session_state.df_orders = get_sheet_data("orders")
if "current_user" not in st.session_state: st.session_state.current_user = None

if st.button(T["refresh_btn"], use_container_width=True):
    st.session_state.df_users = get_sheet_data("users")
    st.session_state.df_trades = get_sheet_data("trades")
    st.session_state.df_codes = get_sheet_data("codes")
    st.session_state.df_claimed = get_sheet_data("claimed_codes")
    st.session_state.df_orders = get_sheet_data("orders")
    st.session_state.df_tps = get_sheet_data("tps")
    st.rerun()

# Authentication UI
st.sidebar.header(T["auth_header"])
if st.session_state.current_user is None:
    auth_action = st.sidebar.radio(T["choose_action"], [T["login"], T["register"]])
    auth_user = st.sidebar.text_input(T["username"]).strip().lower()
    auth_pass = st.sidebar.text_input(T["password"], type="password")
    
    if auth_action == T["login"]:
        if st.sidebar.button(T["login"]):
            df = st.session_state.df_users
            user_row = df[df['username'].astype(str).str.strip().str.lower() == auth_user]
            if not user_row.empty and str(user_row.iloc[0]['password']).strip() == str(auth_pass).strip():
                st.session_state.current_user = auth_user
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials.")
    else:
        if st.sidebar.button(T["register"]):
            df = st.session_state.df_users
            if not auth_user or not auth_pass: st.sidebar.error("Fields cannot be empty.")
            elif auth_user in df['username'].astype(str).str.lower().values: st.sidebar.error("Username already exists.")
            else:
                new_user = pd.DataFrame([{"username": auth_user, "password": auth_pass}])
                st.session_state.df_users = pd.concat([df, new_user], ignore_index=True)
                save_sheet_data(st.session_state.df_users, "users")
                st.rerun()
else:
    st.sidebar.success(f"Logged in as: **{st.session_state.current_user}**")
    
    # ─── PASSWORD MANAGEMENT BLOCK (USER SELF-SERVICE & ADMIN OVERRIDE) ───
    with st.sidebar.expander("🔑 Password Settings" if lang == "English" else "🔑 Nastavení Hesla"):
        df_u = st.session_state.df_users
        if st.session_state.current_user == "admin":
            st.markdown("**Admin Master Override**")
            target_player = st.selectbox("Select Player Account", df_u['username'].astype(str).values)
            new_override_pass = st.text_input("Set New Password for Player", type="password")
            if st.button("Force Apply Reset"):
                if new_override_pass:
                    df_u.loc[df_u['username'].astype(str) == target_player, 'password'] = new_override_pass
                    st.session_state.df_users = df_u
                    save_sheet_data(df_u, "users")
                    st.success(f"Password updated for {target_player}!")
        else:
            self_new_pass = st.text_input("Enter New Password", type="password")
            if st.button("Update My Password"):
                if self_new_pass:
                    df_u.loc[df_u['username'].astype(str) == st.session_state.current_user, 'password'] = self_new_pass
                    st.session_state.df_users = df_u
                    save_sheet_data(df_u, "users")
                    st.success("Your password has been changed!")
                    
    if st.sidebar.button(T["logout"]):
        st.session_state.current_user = None
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(T["tabs"])

# ==========================================
# TAB 1: MARKETPLACE / OBCHOD
# ==========================================
with tab1:
    st.header(T["marketplace"])
    df_trades = st.session_state.df_trades
    df_codes = st.session_state.df_codes
    df_claimed = st.session_state.df_claimed
    
    if st.session_state.current_user:
        with st.expander(T["create_listing"]):
            selected_item_key = st.selectbox(T["item_name"], list(PRICE_SUGGESTIONS.keys()))
            suggested_val, suggested_amount = PRICE_SUGGESTIONS[selected_item_key]
            
            if selected_item_key == "Custom Item / Jiný předmět":
                final_item_name = st.text_input(T["custom_item"]).strip()
            else:
                final_item_name = selected_item_key
                st.caption(f"{T['suggested']} **{suggested_val} {T['diamonds']}** | Qty: **{suggested_amount}x**")
            
            item_amount_val = st.number_input(T["item_amount"], min_value=1, value=suggested_amount)
            is_enchantable = st.checkbox(T["enchantable"])
            enchants = []
            if is_enchantable:
                text_input = st.text_input(T["enchants_placeholder"])
                enchants = [e.strip() for e in text_input.split(",") if e.strip()]
            
            listing_type = st.radio(T["format"], [T["fixed_price"], T["auction_format"]])
            st.markdown(T["duration_settings"])
            is_permanent = st.checkbox(T["stay_forever"], value=False)
            
            duration_amount = 2
            duration_unit = "Hours" if lang == "English" else "Hodiny"
            if not is_permanent:
                col_dur, col_unit = st.columns([2, 2])
                with col_dur: duration_amount = st.number_input(T["time_amount"], min_value=1, value=2)
                with col_unit: duration_unit = st.selectbox(T["time_unit"], ["Minutes", "Hours", "Days"] if lang == "English" else ["Minuty", "Hodiny", "Dny"], index=1)
                
            if listing_type == T["fixed_price"]:
                base_price_val = st.number_input(T["base_price"], min_value=1, value=suggested_val if suggested_val > 0 else 10)
                price_string = f"{base_price_val} Diamonds"
                is_auction_val = False
            else:
                base_price_val = st.number_input(T["start_bid"], min_value=1, value=suggested_val if suggested_val > 0 else 5)
                price_string = f"Starting bid: {base_price_val} Diamonds"
                is_auction_val = True
            
            if st.button(T["publish"]):
                if final_item_name:
                    next_id = int(df_trades["id"].max() + 1) if not df_trades.empty and 'id' in df_trades.columns else 1
                    exp_time = "Permanent" if is_permanent else (datetime.now() + calculate_delta(duration_amount, duration_unit)).isoformat()
                    
                    new_trade = pd.DataFrame([{
                        "id": next_id, "seller": st.session_state.current_user, "item": final_item_name,
                        "amount": int(item_amount_val), "enchants": str(enchants), "price": price_string,
                        "created_at": datetime.now().isoformat(), "expires_at": exp_time, "sale_price": "",
                        "sale_at": "", "is_auction": is_auction_val, "highest_bid": base_price_val if is_auction_val else "", "highest_bidder": ""
                    }])
                    st.session_state.df_trades = pd.concat([df_trades, new_trade], ignore_index=True)
                    save_sheet_data(st.session_state.df_trades, "trades")
                    st.rerun()

    st.subheader(T["active_listings"])
    global_promo_input = st.text_input(T["global_coupon_label"], placeholder=T["global_coupon_placeholder"]).strip().upper() if st.session_state.current_user else ""

    if df_trades.empty or 'item' not in df_trades.columns:
        st.write(T["no_items"])
    else:
        for idx, row in df_trades.iterrows():
            col1, col2 = st.columns([4, 2])
            display_price = str(row.get('price', 'Free'))
            item_name_lower = str(row.get('item', '')).lower()
            row_id_str = str(row.get('id', '')).strip()
            
            code_success_msg = None
            if global_promo_input and not df_codes.empty:
                matched_code = df_codes[df_codes['code'].astype(str).str.upper() == global_promo_input]
                if not matched_code.empty:
                    code_row = matched_code.iloc[0]
                    discount_amt = int(code_row.get('discount', 0))
                    max_allowed = int(code_row.get('max_uses', 1)) if pd.notna(code_row.get('max_uses')) and str(code_row.get('max_uses')).strip() != "" else 1
                    
                    times_used = 0
                    if not df_claimed.empty and "code" in df_claimed.columns:
                        times_used = len(df_claimed[(df_claimed['username'].astype(str) == str(st.session_state.current_user)) & (df_claimed['code'].astype(str).str.upper() == global_promo_input)])
                    
                    is_banned = False
                    if pd.notna(code_row.get('banned_items')) and str(code_row.get('banned_items')).strip():
                        banned_tokens = [bk.strip().lower() for bk in str(code_row['banned_items']).split(",") if bk.strip()]
                        for token in banned_tokens:
                            if token == row_id_str or token in item_name_lower: is_banned = True

                    if is_banned: code_success_msg = "BLOCKED_BLACKLIST"
                    elif times_used >= max_allowed: code_success_msg = "ALREADY_USED"
                    else:
                        base_num = extract_numeric_price(display_price)
                        display_price = f"✨ {round(base_num * (1 - discount_amt / 100))} Diamonds ({discount_amt}% OFF)"
                        code_success_msg = f"{T['code_success']}"

            with col1:
                st.markdown(f"**🛒 ID {row['id']}: {row['seller']} is selling {row['item']} ({row['amount']}x)**")
                st.markdown(f"Price: **{display_price}**")
                if code_success_msg == "BLOCKED_BLACKLIST": st.error(T["code_blocked_msg"])
                elif code_success_msg == "ALREADY_USED": st.error(T["code_already_used"])
                elif code_success_msg: st.success(code_success_msg)
            with col2:
                if st.session_state.current_user in ["admin", row.get('seller')]:
                    if st.button(T["remove_listing"], key=f"del_{row['id']}"):
                        st.session_state.df_trades = df_trades.drop(idx)
                        save_sheet_data(st.session_state.df_trades, "trades")
                        st.rerun()
            st.divider()

# ==========================================
# TAB 2: PRODUCTION ORDERS / ZAKÁZKY (FLEXIBLE INCREMENTS + FIXED CLOSE)
# ==========================================
with tab2:
    st.header(lang == "English" and "📜 Production & Delivery Orders Board" or "📜 Zakázky & Objednávky")
    df_orders = st.session_state.df_orders
    
    if st.session_state.current_user:
        with st.expander(lang == "English" and "➕ Request New Supply Order" or "➕ Vytvořit novou zakázku"):
            req_item = st.text_input(lang == "English" and "Requested Item" or "Požadovaný Předmět").strip()
            req_qty = st.number_input(lang == "English" and "Target Qty" or "Cílové množství", min_value=1, value=80)
            req_reward = st.number_input(lang == "English" and "Reward (Diamonds)" or "Odměna (Diamanty)", min_value=1, value=5)
            if st.button(lang == "English" and "Broadcast Request" or "Odeslat objednávku"):
                next_oid = int(df_orders["id"].max() + 1) if not df_orders.empty else 1
                new_o = pd.DataFrame([{"id": next_oid, "buyer": st.session_state.current_user, "item": req_item, "target_qty": req_qty, "current_qty": 0, "reward_diamonds": req_reward}])
                st.session_state.df_orders = pd.concat([df_orders, new_o], ignore_index=True)
                save_sheet_data(st.session_state.df_orders, "orders")
                st.rerun()

    # Re-engineered rendering flow using target index lookups to ensure deletions sync flawlessly
    if df_orders.empty:
        st.write("No active production orders.")
    else:
        for idx in range(len(df_orders)):
            o_row = df_orders.iloc[idx]
            order_id = o_row['id']
            
            st.markdown(f"### 📦 Order #{order_id}: `{o_row['buyer']}` needs **{o_row['item']}**")
            curr, target = int(o_row['current_qty']), int(o_row['target_qty'])
            st.progress(min(1.0, curr/target))
            st.write(f"Status: {curr} / {target} ({max(0, target-curr)} remaining) | Reward: {o_row['reward_diamonds']} 💎")
            
            if st.session_state.current_user in ["admin", o_row['buyer']]:
                c_val, c_del = st.columns([3, 1])
                with c_val:
                    # ─── INCREMENT UPGRADE: CHOOSE CUSTOM VALUE INSTEAD OF ONLY +1 ───
                    new_curr_input = st.number_input(f"Update Shipped Qty (Order #{order_id})", min_value=0, max_value=target, value=curr, key=f"inp_{order_id}")
                    if new_curr_input != curr:
                        st.session_state.df_orders.loc[st.session_state.df_orders['id'] == order_id, 'current_qty'] = new_curr_input
                        save_sheet_data(st.session_state.df_orders, "orders")
                        st.rerun()
                with c_del:
                    # ─── REMOVAL UPGRADE: CLEAN DATA DELETION TRACKING BY UNIQUE ID ───
                    if st.button("❌ Close Board", key=f"close_{order_id}", use_container_width=True):
                        st.session_state.df_orders = st.session_state.df_orders[st.session_state.df_orders['id'] != order_id]
                        save_sheet_data(st.session_state.df_orders, "orders")
                        st.rerun()
            st.divider()

# ==========================================
# TAB 3: TRACKER & ARRESTS / TRESTY
# ==========================================
with tab3:
    st.header(lang == "English" and "⚡ Teleport Tracker & ⚖️ Arrest Record Logs" or "⚡ Tracker portů a ⚖️ Evidence Trestů")
    df_tps = st.session_state.df_tps
    
    st.subheader(lang == "English" and "🕵️ Teleport Quota Checker" or "🕵️ Kontrola kvóty teleportů")
    tp_username = st.text_input(lang == "English" and "Player Minecraft Account Name" or "Minecraft jméno hráče").strip().lower()
    if tp_username:
        if df_tps.empty or 'username' not in df_tps.columns:
            df_tps = pd.DataFrame(columns=["username", "remaining_tps", "jail_reason", "jail_until"])
            
        user_row = df_tps[df_tps['username'].astype(str).str.lower() == tp_username]
        if user_row.empty:
            new_tp = pd.DataFrame([{"username": tp_username, "remaining_tps": MAX_TPS, "jail_reason": "", "jail_until": ""}])
            df_tps = pd.concat([df_tps, new_tp], ignore_index=True)
            save_sheet_data(df_tps, "tps")
            curr_tps = MAX_TPS
        else:
            curr_tps = int(user_row.iloc[0]['remaining_tps'])
        st.metric(lang == "English" and "Teleports Available Today" or "Dnes zbývající teleporty", f"{curr_tps} / {MAX_TPS}")

    st.markdown("---")
    
    st.subheader(lang == "English" and "⚖️ Server Prison & Jail Registry" or "⚖️ Serverový Vězeňský Rejstřík (Tresty)")
    if st.session_state.current_user == "admin":
        with st.expander(lang == "English" and "🚨 Sentence Player to Jail" or "🚨 Uvěznit / Potrestat hráče"):
            jail_user = st.text_input(lang == "English" and "Convicted Player Username" or "Uživatelské jméno hříšníka").strip().lower()
            jail_reason = st.text_input(lang == "English" and "Crime / Reason for Sentence" or "Důvod trestu / Přestupek")
            jail_duration = st.number_input(lang == "English" and "Sentence Duration (Hours)" or "Doba trestu (v hodinách)", min_value=1, value=24)
            
            if st.button(lang == "English" and "Execute Arrest Warrant" or "Uplatnit trest"):
                if jail_user:
                    until_time = (datetime.now() + timedelta(hours=jail_duration)).isoformat()
                    if not df_tps.empty and jail_user in df_tps['username'].astype(str).str.lower().values:
                        idx = df_tps[df_tps['username'].astype(str).str.lower() == jail_user].index[0]
                        df_tps.at[idx, 'jail_reason'] = jail_reason
                        df_tps.at[idx, 'jail_until'] = until_time
                    else:
                        new_jail = pd.DataFrame([{"username": jail_user, "remaining_tps": MAX_TPS, "jail_reason": jail_reason, "jail_until": until_time}])
                        df_tps = pd.concat([df_tps, new_jail], ignore_index=True)
                    st.session_state.df_tps = df_tps
                    save_sheet_data(df_tps, "tps")
                    st.success(f"⚖️ {jail_user} configuration updated.")
                    st.rerun()

    if not df_tps.empty and "jail_until" in df_tps.columns:
        active_jails = df_tps[df_tps['jail_until'].astype(str).str.strip() != ""]
        if not active_jails.empty:
            for j_idx, j_row in active_jails.iterrows():
                st.warning(f"🔒 **{j_row['username'].upper()}**")
                st.write(f"**{lang == 'English' and 'Reason' or 'Důvod'}:** {j_row['jail_reason']}")
                st.caption(f"Remaining: {format_time_remaining(j_row['jail_until'])}")
                if st.session_state.current_user == "admin":
                    if st.button("Pardon / Release", key=f"unjail_{j_row['username']}"):
                        df_tps.at[j_idx, 'jail_reason'] = ""
                        df_tps.at[j_idx, 'jail_until'] = ""
                        save_sheet_data(df_tps, "tps")
                        st.rerun()

# ==========================================
# TAB 4: CODES / SLEVOVÉ KÓDY (WITH ADMIN DELETION SUPPORTS)
# ==========================================
with tab4:
    st.header(T["code_header"])
    df_codes = st.session_state.df_codes
    df_trades = st.session_state.df_trades
    is_admin = st.session_state.current_user == "admin"
    
    if st.session_state.current_user:
        with st.expander(T["create_code"]):
            new_code_str = st.text_input(T["code_input"], value="VOLBA25").strip().upper()
            code_discount = st.slider(T["code_pct"], 1, 100, 15)
            selected_scope = st.radio(T["code_scope"], [T["scope_global"], T["scope_choose_one"], T["scope_specific"]])
            
            target_ids_val = "GLOBAL"
            if selected_scope == T["scope_choose_one"]: target_ids_val = "CHOOSE_ONE"
            elif selected_scope == T["scope_specific"]: target_ids_val = st.text_input(T["specific_help"]).strip()
                
            banned_items_input = st.text_input(T["code_banned_expl"])
            usage_limit = st.slider("Usage Limit per Player" if lang == "English" else "Limit použití na hráče", min_value=1, max_value=10, value=1)
                
            if st.button(T["btn_create_code"]):
                if new_code_str:
                    passed_ownership_check = True
                    banned_tokens = [t.strip() for t in banned_items_input.split(",") if t.strip()]
                    for token in banned_tokens:
                        if token.isdigit():
                            matched_listing = df_trades[df_trades['id'].astype(float) == float(token)]
                            if not matched_listing.empty:
                                if str(matched_listing.iloc[0].get('seller', '')).strip().lower() != st.session_state.current_user.lower() and st.session_state.current_user.lower() != "admin":
                                    passed_ownership_check = False
                    
                    if not passed_ownership_check:
                        st.error(T["not_owned_err"])
                    else:
                        new_entry = pd.DataFrame([{"code": new_code_str, "creator": st.session_state.current_user, "discount": code_discount, "target_ids": target_ids_val, "banned_items": banned_items_input.strip(), "max_uses": usage_limit}])
                        st.session_state.df_codes = pd.concat([df_codes, new_entry], ignore_index=True)
                        save_sheet_data(st.session_state.df_codes, "codes")
                        st.rerun()
                    
        # ─── CODE MANAGEMENT VISUAL LIST WITH ADMIN DELETE OPTION ───
        if not df_codes.empty and "code" in df_codes.columns:
            for c_idx, c_row in df_codes.iterrows():
                col_info, col_act = st.columns([4, 1])
                with col_info:
                    st.markdown(f"🎟️ **Code:** `{c_row['code']}` | **Discount:** {c_row['discount']}% | **Creator:** {c_row['creator']}")
                    st.caption(f"Max Player Uses: {c_row.get('max_uses', 1)} | Banned Targets: {c_row.get('banned_items', 'None')}")
                with col_act:
                    if st.session_state.current_user == "admin" or str(c_row.get('creator')).strip().lower() == st.session_state.current_user.lower():
                        if st.button("❌ Remove Code", key=f"del_code_{c_row['code']}"):
                            st.session_state.df_codes = df_codes.drop(c_idx)
                            save_sheet_data(st.session_state.df_codes, "codes")
                            st.rerun()
                st.divider()
