import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date, timedelta
import time

# ─── AUTO-REFRESH CONFIGURATION ──────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# ─── CONFIGURATION & DATA (EXPANDED & REORDERED) ─────────────────
MAX_TPS = 3
TODAY = str(date.today())

PRICE_SUGGESTIONS = {
    "Custom Item / Jiný předmět": 0,
    # ⚔️ High-Tier Gear & Tools
    "Netherite Ingot": 8,
    "Diamond Block": 9,
    "Elytra": 150,
    "Shulker Box": 20,
    "Beacon": 40,
    "Totem of Undying": 30,
    "Nether Star": 30,
    "Ancient Debris": 2,
    "Mending Book": 50,
    "Silk Touch Book": 30,
    "Unbreaking III Book": 30,
    "Efficiency V Book": 40,
    "Trident": 80,
    # 🐾 Animals & Entities
    "Horse (Tamed / High Stats)": 5,
    "Donkey / Mule": 4,
    "Villager (Unemployed)": 6,
    "Mending Villager": 25,
    "Armorer Villager (Master)": 15,
    "Wolf / Dog": 2,
    "Cat": 2,
    "Axolotl (Blue Rare)": 10,
    "Axolotl (Standard)": 2,
    "Bee Nest (With 3 Bees)": 4,
    "Frog / Toad": 2,
    "Camel": 6,
    "Sniffer Egg": 8,
    # 💎 Blocks & Valuables
    "Enchanted Golden Apple": 10,
    "Golden Apple": 1,
    "Block of Netherite": 72,
    "Emerald Block": 2,
    "Gold Block": 3,
    "Iron Block": 1,
    "Sea Lantern (Stack)": 4,
    "Glowstone (Stack)": 2,
    "Crying Obsidian (Stack)": 3,
    # 🧪 Brewing & Mob Drops
    "Wither Skeleton Skull": 5,
    "Sponge Block": 2,
    "Blaze Rod (Stack)": 3,
    "Ender Pearl (Stack)": 2,
    "Gunpowder (Stack)": 3,
    "Phantom Membrane": 1,
    "Slimeball (Stack)": 2,
    "Dragon's Breath": 2
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
        "change_pass_header": "🔒 Change Your Password",
        "new_password": "New Password",
        "update_pass_btn": "Update Password",
        "pass_update_success": "✅ Password updated successfully!",
        "admin_reset_header": "🛡️ Admin Password Reset",
        "select_player": "Select Player",
        "reset_pass_btn": "Reset Player Password",
        "tabs": ["🛒 Trade Store", "📜 Case Records", "⚡ Teleport Tracker", "🎟️ Sale Codes"],
        "marketplace": "Server Marketplace",
        "create_listing": "➕ Create Listing (Sale / Sale Delay / Auction)",
        "item_name": "Item Selection (Type to Search)",
        "custom_item": "Enter Custom Item Name",
        "item_amount": "Amount / Quantity",
        "suggested": "💡 Suggested Price:",
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
        "sched_sale": "Schedule a future discount sale?",
        "adv_sale_header": "##### Advanced Scheduled Sale",
        "discount_type": "Discount Type",
        "pct_off_label": "Percentage Off (1-100%)",
        "make_free_label": "Make Free",
        "preview": "📊 Sale Preview: Price will drop from {} Diamonds to **{}**",
        "publish": "Publish Listing",
        "active_listings": "Active Listings",
        "global_coupon_label": "🎟️ Apply Promo / Sale Code for Checkout",
        "global_coupon_placeholder": "Enter code (e.g. CUSTOMERCHOICE) and press Enter",
        "coupon_login_required": "🔒 Please log in to your account to use checkout codes.",
        "no_items": "No items on sale right now.",
        "time_left": "⏳ Time left: {}",
        "forever": "Stay Forever",
        "bid_min": "Bid (Min {})",
        "place_bid": "🔨 Place Bid",
        "manage_exp": "⏳ Manage Expiration",
        "update_exp": "Update Expiration",
        "trigger_sale": "🏷️ Trigger Sale",
        "apply_now": "Apply Sale Now",
        "remove_sale": "🏷️ Remove Sale",
        "remove_listing": "❌ Remove Listing",
        "refresh_btn": "🔄 Force Refresh Data",
        "code_header": "🎟️ Promo & Sale Codes Manager",
        "create_code": "➕ Create New Sale Code",
        "code_input": "Sale Code Name (e.g. CHOOSE25)",
        "code_pct": "Discount Percentage",
        "code_scope": "Code Target Scope",
        "scope_global": "Global (All your items)",
        "scope_choose_one": "Global (Customer chooses 1 item)",
        "scope_admin_global": "Admin Global (All marketplace items)",
        "scope_specific": "Specific Listing IDs only",
        "specific_help": "Enter comma separated IDs (e.g. 1, 4, 12)",
        "btn_create_code": "Generate Code",
        "active_codes": "Active Sale Codes",
        "code_table_cols": ["Code", "Creator", "Discount", "Scope / IDs"],
        "code_success": "✅ Code Applied! Price updated.",
        "code_invalid": "❌ Code invalid for this item.",
        "code_already_used": "⚠️ You have already used this code!",
        "claimed_header": "📊 Used Codes History (Admin & Owners)",
        "claimed_cols": ["User", "Code Used"],
        "clear_code_users": "🔄 Reset Code Usage",
        "clear_success": "Usage limits for this code have been wiped!",
        "delete_code_label": "❌ Delete Code permanently",
        "delete_code_success": "The code has been successfully deleted!"
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
        "change_pass_header": "🔒 Změna Vašeho Hesla",
        "new_password": "Nové Heslo",
        "update_pass_btn": "Aktualizovat Heslo",
        "pass_update_success": "✅ Heslo bylo úspěšně změněno!",
        "admin_reset_header": "🛡️ Admin Reset Hesla",
        "select_player": "Vyberte Hráče",
        "reset_pass_btn": "Resetovat Heslo Hráče",
        "tabs": ["🛒 Obchod / Tržiště", "📜 Záznamy Trestů", "⚡ Teleport Tracker", "🎟️ Slevové Kódy"],
        "marketplace": "Serverové Tržiště",
        "create_listing": "➕ Vytvořit Nabídku (Sleva / Zpožděný prodej / Aukce)",
        "item_name": "Výběr Předmětu (Pište pro hledání)",
        "custom_item": "Zadejte vlastní název předmětu",
        "item_amount": "Množství / Počet",
        "suggested": "💡 Doporučená cena:",
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
        "sched_sale": "Naplánovat budoucí slevu?",
        "adv_sale_header": "##### Pokročilý Naplánovaný Prodej",
        "discount_type": "Typ Slevy",
        "pct_off_label": "Procentuální Sleva (1-100%)",
        "make_free_label": "Zdarma",
        "preview": "📊 Náhled slevy: Cena klesne z {} Diamantů na **{}**",
        "publish": "Publikovat Nabídku",
        "active_listings": "Aktivní Nabídky",
        "global_coupon_label": "🎟️ Použít slevový / promo kód pro nákup",
        "global_coupon_placeholder": "Zadejte kód a stiskněte Enter",
        "coupon_login_required": "🔒 Pro uplatnění slevových kódů se musíte přihlásit.",
        "no_items": "Momentálně nejsou v nabídce žádné položky.",
        "time_left": "⏳ Zbývající čas: {}",
        "forever": "Navždy",
        "bid_min": "Příhoz (Min {})",
        "place_bid": "🔨 Přihodit",
        "manage_exp": "⏳ Spravovat Expiraci",
        "update_exp": "Aktualizovat Expiraci",
        "trigger_sale": "🏷️ Aktivovat Slevu",
        "apply_now": "Použít Slevu Ihned",
        "remove_sale": "🏷️ Odstranit Slevu",
        "remove_listing": "❌ Odstranit Nabídku",
        "refresh_btn": "🔄 Vynutit Obnovení Dat",
        "code_header": "🎟️ Správce Slevových Kódů",
        "create_code": "➕ Vytvořit Nový Slevový Kód",
        "code_input": "Název kódu (např. VOLBA25)",
        "code_pct": "Výše slevy v procentech",
        "code_scope": "Rozsah Platnosti Kódu",
        "scope_global": "Globální (Všechny moje předměty)",
        "scope_choose_one": "Globální (Zákazník si vybere 1 položku)",
        "scope_admin_global": "Admin Globální (Všechny předměty na trhu)",
        "scope_specific": "Pouze specifické ID nabídek",
        "specific_help": "Zadejte ID oddělená čárkou (např. 1, 4, 12)",
        "btn_create_code": "Generovat Kód",
        "active_codes": "Aktivní Slevové Kódy",
        "code_table_cols": ["Kód", "Tvůrce", "Sleva", "Rozsah / ID"],
        "code_success": "✅ Kód uplatněn! Cena byla upravena.",
        "code_invalid": "❌ Neplatný slevový kód pro tuto položku.",
        "code_already_used": "⚠️ Tento kód jsi již jednou použil!",
        "claimed_header": "📊 Historie Použití Kódů (Admin & Vlastníci)",
        "claimed_cols": ["Uživatel", "Použitý Kód"],
        "clear_code_users": "🔄 Obnovit limit použití kódu",
        "clear_success": "Limity použití pro tento kód byly smazány!",
        "delete_code_label": "❌ Smazat kód navždy",
        "delete_code_success": "Slevový kód byl úspěšně odstraněn ze systému!"
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
        cols = ["code", "creator", "discount", "target_ids"]
    elif worksheet_name == "claimed_codes":
        cols = ["username", "code"]
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
    except:
        pass

def calculate_delta(amount, unit):
    if unit in ["Minutes", "Minuty"]:
        return timedelta(minutes=amount)
    elif unit in ["Hours", "Hodiny"]:
        return timedelta(hours=amount)
    else:
        return timedelta(days=amount)

def format_time_remaining(target_iso):
    if pd.isna(target_iso) or str(target_iso).strip() in ["", "nan", "Permanent"]:
        return T["forever"]
    try:
        delta = datetime.fromisoformat(str(target_iso)) - datetime.now()
        total_seconds = delta.total_seconds()
        if total_seconds <= 0:
            return "Expired"
        if total_seconds < 3600:
            return f"{round(total_seconds / 60, 1)}m"
        elif total_seconds < 86400:
            return f"{round(total_seconds / 3600, 1)}h"
        else:
            return f"{round(total_seconds / 86400, 1)}d"
    except:
        return T["forever"]

def extract_numeric_price(price_str):
    try:
        clean_num = int(''.join(filter(str.isdigit, str(price_str))))
        return clean_num
    except:
        return 0

def calculate_sale_display(base_val, sale_mode, pct_off):
    if sale_mode in ["Make Free", "Zdarma"] or pct_off == 100:
        return "Free (100% OFF)" if lang == "English" else "Zdarma (100% SLEVA)"
    clean_base = extract_numeric_price(base_val)
    final_num = round(clean_base * (1 - pct_off / 100))
    suffix = "Diamonds" if lang == "English" else "Diamantů"
    off_suffix = "OFF" if lang == "English" else "SLEVA"
    return f"{final_num} {suffix} ({pct_off}% {off_suffix})"

# Initialize structures
if "df_users" not in st.session_state:
    st.session_state.df_users = get_sheet_data("users")
if "df_trades" not in st.session_state:
    st.session_state.df_trades = get_sheet_data("trades")
if "df_codes" not in st.session_state:
    st.session_state.df_codes = get_sheet_data("codes")
if "df_claimed" not in st.session_state:
    st.session_state.df_claimed = get_sheet_data("claimed_codes")
if "df_tps" not in st.session_state:
    st.session_state.df_tps = get_sheet_data("tps")
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Timer cleanup
df_trades_current = st.session_state.df_trades
if not df_trades_current.empty and "expires_at" in df_trades_current.columns:
    now_str = datetime.now().isoformat()
    expires_str_series = df_trades_current["expires_at"].astype(str).str.strip()
    valid_trades = df_trades_current[
        (df_trades_current["expires_at"].isna()) | 
        (expires_str_series == "") | 
        (expires_str_series == "nan") | 
        (expires_str_series == "Permanent") | 
        (expires_str_series > now_str)
    ]
    if len(valid_trades) != len(df_trades_current):
        st.session_state.df_trades = valid_trades
        save_sheet_data(valid_trades, "trades")

if st.button(T["refresh_btn"], use_container_width=True):
    st.session_state.df_users = get_sheet_data("users")
    st.session_state.df_trades = get_sheet_data("trades")
    st.session_state.df_codes = get_sheet_data("codes")
    st.session_state.df_claimed = get_sheet_data("claimed_codes")
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
            if not auth_user or not auth_pass:
                st.sidebar.error("Fields cannot be empty.")
            elif auth_user in df['username'].astype(str).str.lower().values:
                st.sidebar.error("Username already exists.")
            else:
                new_user = pd.DataFrame([{"username": auth_user, "password": auth_pass}])
                st.session_state.df_users = pd.concat([df, new_user], ignore_index=True)
                save_sheet_data(st.session_state.df_users, "users")
                st.rerun()
else:
    st.sidebar.success(f"Logged in as: **{st.session_state.current_user}**")
    if st.sidebar.button(T["logout"]):
        st.session_state.current_user = None
        st.rerun()
        
    st.sidebar.markdown("---")
    
    st.sidebar.subheader(T["change_pass_header"])
    new_pass_input = st.sidebar.text_input(T["new_password"], type="password", key="owner_change_pass_field")
    if st.sidebar.button(T["update_pass_btn"], key="owner_change_pass_btn"):
        if new_pass_input.strip():
            df_u = st.session_state.df_users
            user_clean = str(st.session_state.current_user).strip().lower()
            matched_indices = df_u[df_u['username'].astype(str).str.strip().str.lower() == user_clean].index
            if not matched_indices.empty:
                df_u.at[matched_indices[0], 'password'] = str(new_pass_input).strip()
                st.session_state.df_users = df_u
                save_sheet_data(df_u, "users")
                st.sidebar.success(T["pass_update_success"])
                time.sleep(1)
                st.rerun()

    if st.session_state.current_user == "admin":
        st.sidebar.markdown("---")
        st.sidebar.subheader(T["admin_reset_header"])
        df_u = st.session_state.df_users
        if not df_u.empty and 'username' in df_u.columns:
            player_list = sorted(list(df_u['username'].astype(str).str.strip().values))
            selected_player_to_reset = st.sidebar.selectbox(T["select_player"], player_list, key="admin_sb_p_reset")
            admin_new_pass = st.sidebar.text_input(T["new_password"], type="password", key="admin_txt_p_reset")
            if st.sidebar.button(T["reset_pass_btn"], key="admin_btn_p_reset"):
                if selected_player_to_reset and admin_new_pass.strip():
                    matched_admin_idx = df_u[df_u['username'].astype(str).str.strip() == str(selected_player_to_reset)].index
                    if not matched_admin_idx.empty:
                        df_u.at[matched_admin_idx[0], 'password'] = str(admin_new_pass).strip()
                        st.session_state.df_users = df_u
                        save_sheet_data(df_u, "users")
                        st.sidebar.success(f"Successfully reset password for {selected_player_to_reset}!")
                        time.sleep(1)
                        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(T["tabs"])

# ==========================================
# TAB 1: MARKETPLACE
# ==========================================
with tab1:
    st.header(T["marketplace"])
    df_trades = st.session_state.df_trades
    df_codes = st.session_state.df_codes
    df_claimed = st.session_state.df_claimed
    
    if st.session_state.current_user:
        with st.expander(T["create_listing"]):
            selected_item_key = st.selectbox(
                T["item_name"], 
                list(PRICE_SUGGESTIONS.keys()),
                help="Type to search through available suggestions / Zapište pro vyhledávání v doporučeních"
            )
            
            if selected_item_key == "Custom Item / Jiný předmět":
                final_item_name = st.text_input(T["custom_item"], placeholder="e.g. Diamond Sword with Fire Aspect").strip()
                suggested_val = 0
            else:
                final_item_name = selected_item_key
                suggested_val = PRICE_SUGGESTIONS[selected_item_key]
                st.caption(f"{T['suggested']} **{suggested_val} {T['diamonds']}**")
            
            item_amount_val = st.number_input(T["item_amount"], min_value=1, value=1, step=1)
                
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
                with col_dur:
                    duration_amount = st.number_input(T["time_amount"], min_value=1, value=2)
                with col_unit:
                    duration_unit = st.selectbox(T["time_unit"], ["Minutes", "Hours", "Days"] if lang == "English" else ["Minuty", "Hodiny", "Dny"], index=1)
                
            if listing_type == T["fixed_price"]:
                base_price_val = st.number_input(T["base_price"], min_value=1, value=suggested_val if suggested_val > 0 else 10)
                has_delayed_sale = st.checkbox(T["sched_sale"])
                sale_price_val = ""
                sale_at_val = ""
                if has_delayed_sale:
                    st.markdown(T["adv_sale_header"])
                    sale_mode = st.radio(T["discount_type"], [T["pct_off_label"], T["make_free_label"]], key="sched_mode")
                    discount_pct = st.slider("Select %", min_value=1, max_value=100, value=20, key="sched_pct") if sale_mode == T["pct_off_label"] else 100
                    calculated_price = calculate_sale_display(base_price_val, sale_mode, discount_pct)
                    st.info(T["preview"].format(base_price_val, calculated_price))
                    
                    col_sdur, col_sunit = st.columns([2, 2])
                    with col_sdur:
                        delay_amount = st.number_input(T["time_amount"], min_value=1, value=30, key="sched_amt")
                    with col_sunit:
                        delay_unit = st.selectbox(T["time_unit"], ["Minutes", "Hours", "Days"] if lang == "English" else ["Minuty", "Hodiny", "Dny"], key="sched_unit")
                        
                    sale_price_val = calculated_price
                    sale_at_val = (datetime.now() + calculate_delta(delay_amount, delay_unit)).isoformat()
                
                price_string = f"{base_price_val} Diamonds"
                is_auction_val = False
            else:
                base_price_val = st.number_input(T["start_bid"], min_value=1, value=suggested_val if suggested_val > 0 else 5)
                price_string = f"Starting bid: {base_price_val} Diamonds"
                sale_price_val = ""
                sale_at_val = ""
                is_auction_val = True
            
            if st.button(T["publish"]):
                if final_item_name:
                    next_id = int(df_trades["id"].max() + 1) if not df_trades.empty and 'id' in df_trades.columns else 1
                    exp_time = "Permanent" if is_permanent else (datetime.now() + calculate_delta(duration_amount, duration_unit)).isoformat()
                    
                    new_trade = pd.DataFrame([{
                        "id": next_id,
                        "seller": st.session_state.current_user,
                        "item": final_item_name,
                        "amount": int(item_amount_val),
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
                    st.rerun()

    st.subheader(T["active_listings"])
    
    # 🔒 AUTH PROTECTION: Only logged-in accounts can submit checkouts
    if st.session_state.current_user:
        global_promo_input = st.text_input(T["global_coupon_label"], placeholder=T["global_coupon_placeholder"], key="global_promo_checkout_field").strip().upper()
    else:
        st.warning(T["coupon_login_required"])
        global_promo_input = ""

    if df_trades.empty or 'item' not in df_trades.columns:
        st.write(T["no_items"])
    else:
        search_query = st.text_input("🔍 Search items or sellers / Hledat předměty nebo prodejce", "").strip().lower()
        
        now_str = datetime.now().isoformat()
        for idx, row in df_trades.iterrows():
            item_name_lower = str(row.get('item', '')).lower()
            seller_name_lower = str(row.get('seller', '')).lower()
            
            if search_query and (search_query not in item_name_lower and search_query not in seller_name_lower):
                continue
                
            col1, col2 = st.columns([4, 2])
            
            display_price = str(row.get('price', 'Free'))
            has_any_sale_configured = pd.notna(row.get('sale_at')) and row['sale_at'] != ""
            
            if has_any_sale_configured:
                if now_str >= str(row['sale_at']):
                    display_price = f"{row['sale_price']} (Was {row['price']})"
                else:
                    time_info = format_time_remaining(row['sale_at'])
                    display_price += f" (Drops to {row['sale_price']} in {time_info})"

            raw_amt = row.get('amount')
            amt_badge = f" ({int(raw_amt)}x)" if pd.notna(raw_amt) and str(raw_amt).strip() != "" else ""

            # Check if promo code applies dynamically to this specific loop item
            code_success_msg = None
            if global_promo_input and not df_codes.empty:
                matched_code = df_codes[df_codes['code'].astype(str).str.upper() == global_promo_input]
                if not matched_code.empty:
                    code_row = matched_code.iloc[0]
                    creator = str(code_row.get('creator', ''))
                    scope = str(code_row.get('target_ids', 'GLOBAL'))
                    discount_amt = int(code_row.get('discount', 0))
                    code_name_clean = str(code_row.get('code', '')).upper()
                    
                    user_clean = str(st.session_state.current_user)
                    already_used = False
                    if not df_claimed.empty and "code" in df_claimed.columns:
                        matched_claims = df_claimed[
                            (df_claimed['username'].astype(str) == user_clean) & 
                            (df_claimed['code'].astype(str).str.upper() == code_name_clean)
                        ]
                        if not matched_claims.empty:
                            already_used = True
                    
                    if already_used:
                        code_success_msg = "ALREADY_USED"
                    else:
                        is_valid_code = False
                        # Regular complete global scopes
                        if creator == "admin" and scope in ["GLOBAL", "CHOOSE_ONE"]:
                            is_valid_code = True
                        elif creator == row['seller'] and scope in ["GLOBAL", "CHOOSE_ONE"]:
                            is_valid_code = True
                        elif scope not in ["GLOBAL", "CHOOSE_ONE"] and scope != "":
                            # Specific ID-only listings match
                            parsed_ids = [id_item.strip() for id_item in scope.split(",") if id_item.strip()]
                            if str(row['id']) in parsed_ids:
                                is_valid_code = True
                                
                        if is_valid_code and discount_amt > 0:
                            base_num = extract_numeric_price(display_price)
                            price_after_code = round(base_num * (1 - discount_amt / 100))
                            
                            # DYNAMIC LIVE CLIENT INTERFACE PREVIEW OVERWRITE
                            display_price = f"✨ {price_after_code} Diamonds ({discount_amt}% PROMO CODE OFF)"
                            code_success_msg = f"{T['code_success']} ({discount_amt}% OFF)"
                            
                            if f"last_logged_{row['id']}" not in st.session_state or st.session_state[f"last_logged_{row['id']}"] != code_name_clean:
                                new_claim = pd.DataFrame([{"username": user_clean, "code": code_name_clean}])
                                st.session_state.df_claimed = pd.concat([df_claimed, new_claim], ignore_index=True)
                                save_sheet_data(st.session_state.df_claimed, "claimed_codes")
                                st.session_state[f"last_logged_{row['id']}"] = code_name_clean

            with col1:
                if str(row.get('is_auction')) == "True" or row.get('is_auction') is True:
                    st.markdown(f"**🏆 [AUCTION] ID {row['id']}: {row['seller']}'s {row['item']}{amt_badge}**")
                    st.caption(f"Enchants: {row.get('enchants', 'None')}")
                    if row.get('highest_bidder'):
                        st.markdown(f"Current Bid: **{row['highest_bid']} Diamonds** by `{row['highest_bidder']}`")
                    else:
                        st.markdown(f"Starting Bid: **{row['highest_bid']} Diamonds**")
                else:
                    st.markdown(f"**🛒 ID {row['id']}: {row['seller']} is selling {row['item']}{amt_badge}**")
                    st.markdown(f"Price: **{display_price}**")
                    st.caption(f"Enchants: {row.get('enchants', 'None')}")
                
                if code_success_msg == "ALREADY_USED":
                    st.error(T["code_already_used"])
                elif code_success_msg:
                    st.success(code_success_msg)

                exp_status = format_time_remaining(row.get('expires_at'))
                st.caption(T["time_left"].format(exp_status))
            
            with col2:
                is_admin = st.session_state.current_user == "admin"
                is_seller = st.session_state.current_user == row.get('seller', '')
                is_item_auction = str(row.get('is_auction')) == "True" or row.get('is_auction') is True
                
                if is_item_auction and st.session_state.current_user:
                    if st.session_state.current_user != row['seller']:
                        min_bid = int(row['highest_bid']) + 1
                        bid_amount = st.number_input(T["bid_min"].format(min_bid), min_value=min_bid, step=1, key=f"bid_val_{row['id']}")
                        if st.button(T["place_bid"], key=f"bid_btn_{row['id']}"):
                            df_trades.at[idx, 'highest_bid'] = bid_amount
                            df_trades.at[idx, 'highest_bidder'] = st.session_state.current_user
                            st.session_state.df_trades = df_trades
                            save_sheet_data(df_trades, "trades")
                            st.rerun()
                
                if not is_item_auction and (is_seller or is_admin):
                    with st.expander(T["manage_exp"]):
                        mod_perm = st.checkbox(T["stay_forever"], value=("Permanent" in exp_status or pd.isna(row.get('expires_at')) or str(row.get('expires_at')) == ""), key=f"mod_perm_{row['id']}")
                        if not mod_perm:
                            col_m_amt, col_m_unit = st.columns(2)
                            with col_m_amt:
                                mod_amount = st.number_input(T["time_amount"], min_value=1, value=10, key=f"mod_amt_{row['id']}")
                            with col_m_unit:
                                mod_unit = st.selectbox(T["time_unit"], ["Minutes", "Hours", "Days"] if lang == "English" else ["Minuty", "Hodiny", "Dny"], index=1, key=f"mod_unit_{row['id']}")
                        if st.button(T["update_exp"], key=f"mod_exp_btn_{row['id']}"):
                            df_trades.at[idx, 'expires_at'] = "Permanent" if mod_perm else (datetime.now() + calculate_delta(mod_amount, mod_unit)).isoformat()
                            st.session_state.df_trades = df_trades
                            save_sheet_data(df_trades, "trades")
                            st.rerun()

                    if has_any_sale_configured:
                        if st.button(T["remove_sale"], key=f"rm_sale_{row['id']}"):
                            df_trades.at[idx, 'sale_price'] = ""
                            df_trades.at[idx, 'sale_at'] = ""
                            st.session_state.df_trades = df_trades
                            save_sheet_data(df_trades, "trades")
                            st.rerun()
                    else:
                        with st.expander(T["trigger_sale"]):
                            inst_mode = st.radio(T["discount_type"], [T["pct_off_label"], T["make_free_label"]], key=f"inst_mode_{row['id']}")
                            inst_pct = st.slider("Select %", 1, 100, 25, key=f"inst_sld_{row['id']}") if inst_mode == T["pct_off_label"] else 100
                            preview_price = calculate_sale_display(row['price'], inst_mode, inst_pct)
                            if st.button(T["apply_now"], key=f"inst_btn_{row['id']}"):
                                df_trades.at[idx, 'sale_price'] = preview_price
                                df_trades.at[idx, 'sale_at'] = datetime.now().isoformat()
                                st.session_state.df_trades = df_trades
                                save_sheet_data(df_trades, "trades")
                                st.rerun()

                if is_admin or is_seller:
                    if st.button(T["remove_listing"], key=f"del_trade_{row['id']}"):
                        st.session_state.df_trades = df_trades.drop(idx)
                        save_sheet_data(st.session_state.df_trades, "trades")
                        st.rerun()
            st.divider()

# ==========================================
# TAB 2: CASE RECORDS
# ==========================================
with tab2:
    st.header(T["tabs"][1])
    st.info("Held in temporary cache.")

# ==========================================
# TAB 3: TELEPORT TRACKER
# ==========================================
with tab3:
    st.header(T["tabs"][2])
    st.info(f"Date: {TODAY}")
    df_tps = st.session_state.df_tps
    tp_username = st.text_input("Minecraft Username", key="tp_user_input").strip().lower()
    
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
            
        st.metric(label=f"Remaining TPs: {tp_username}", value=f"{current_tps} / {MAX_TPS}")
        
        if st.session_state.current_user == "admin":
            col_use, col_reset = st.columns(2)
            user_idx = df_tps[df_tps['username_clean'] == tp_username].index[0]
            with col_use:
                if st.button("⚡ Use 1 TP", key="btn_use_tp"):
                    if current_tps > 0:
                        df_tps.at[user_idx, 'remaining_tps'] = current_tps - 1
                        st.session_state.df_tps = df_tps
                        save_sheet_data(df_tps, "tps")
                        st.rerun()
            with col_reset:
                if st.button("🔄 Reset TPs", key="btn_reset_tp"):
                    df_tps.at[user_idx, 'remaining_tps'] = MAX_TPS
                    st.session_state.df_tps = df_tps
                    save_sheet_data(df_tps, "tps")
                    st.rerun()

# ==========================================
# TAB 4: ADVANCED SALE CODES (SLEVOVÉ KÓDY)
# ==========================================
with tab4:
    st.header(T["code_header"])
    df_codes = st.session_state.df_codes
    df_claimed = st.session_state.df_claimed
    is_admin = st.session_state.current_user == "admin"
    
    if st.session_state.current_user:
        with st.expander(T["create_code"]):
            new_code_str = st.text_input(T["code_input"]).strip().upper()
            code_discount = st.slider(T["code_pct"], 1, 100, 15)
            
            # Added new custom targeted "CHOOSE_ONE" scope definition selection
            scope_options = [T["scope_global"], T["scope_choose_one"], T["scope_specific"]]
            if is_admin:
                scope_options.insert(0, T["scope_admin_global"])
                
            selected_scope = st.radio(T["code_scope"], scope_options)
            
            target_ids_val = "GLOBAL"
            if selected_scope == T["scope_choose_one"]:
                target_ids_val = "CHOOSE_ONE"
            elif selected_scope == T["scope_specific"]:
                target_ids_val = st.text_input(T["specific_help"]).strip()
                
            if st.button(T["btn_create_code"]):
                if new_code_str:
                    new_code_entry = pd.DataFrame([{
                        "code": new_code_str,
                        "creator": st.session_state.current_user,
                        "discount": code_discount,
                        "target_ids": target_ids_val
                    }])
                    st.session_state.df_codes = pd.concat([df_codes, new_code_entry], ignore_index=True)
                    save_sheet_data(st.session_state.df_codes, "codes")
                    st.success("Sale Code Created Successfully!")
                    st.rerun()
                    
        st.subheader(T["active_codes"])
        if not df_codes.empty and "code" in df_codes.columns:
            private_df = df_codes[is_admin | (df_codes['creator'].astype(str) == st.session_state.current_user)]
            
            if not private_df.empty:
                display_df = private_df.reindex(columns=["code", "creator", "discount", "target_ids"]).fillna("")
                display_df.columns = T["code_table_cols"]
                st.dataframe(display_df, use_container_width=True)
                
                st.markdown("---")
                col_actions_1, col_actions_2 = st.columns(2)
                
                with col_actions_1:
                    st.caption("🔄 **Reset / Refresh Code Claims**")
                    code_to_clear = st.selectbox(T["clear_code_users"], [""] + list(private_df["code"].unique()), key="sb_clear_claims")
                    if code_to_clear and st.button(T["clear_code_users"], key="btn_clear_claims"):
                        if not df_claimed.empty and "code" in df_claimed.columns:
                            updated_claims = df_claimed[df_claimed["code"].astype(str).str.upper() != str(code_to_clear).upper()]
                            st.session_state.df_claimed = updated_claims
                            save_sheet_data(updated_claims, "claimed_codes")
                            st.success(T["clear_success"])
                            st.rerun()
                            
                with col_actions_2:
                    st.caption("🗑️ **Delete Code Matrix Node**")
                    code_to_delete = st.selectbox(T["delete_code_label"], [""] + list(private_df["code"].unique()), key="sb_delete_node")
                    if code_to_delete and st.button(T["delete_code_label"], key="btn_delete_node"):
                        updated_codes = df_codes[df_codes["code"].astype(str).str.upper() != str(code_to_delete).upper()]
                        st.session_state.df_codes = updated_codes
                        save_sheet_data(updated_codes, "codes")
                        
                        if not df_claimed.empty and "code" in df_claimed.columns:
                            updated_claims = df_claimed[df_claimed["code"].astype(str).str.upper() != str(code_to_delete).upper()]
                            st.session_state.df_claimed = updated_claims
                            save_sheet_data(updated_claims, "claimed_codes")
                            
                        st.success(T["delete_code_success"])
                        st.rerun()
            else:
                st.caption("You haven't created any secrets or codes yet!")
        else:
            st.caption("No sale codes are currently active.")
            
        st.subheader(T["claimed_header"])
        if not df_claimed.empty and "code" in df_claimed.columns:
            if is_admin:
                allowed_codes = list(df_codes["code"].unique()) if not df_codes.empty else []
            else:
                allowed_codes = list(df_codes[df_codes["creator"] == st.session_state.current_user]["code"].unique()) if not df_codes.empty else []
                
            visible_claims = df_claimed[df_claimed["code"].str.upper().isin([c.upper() for c in allowed_codes])]
            if not visible_claims.empty:
                display_claims = visible_claims.reindex(columns=["username", "code"])
                display_claims.columns = T["claimed_cols"]
                st.dataframe(display_claims, use_container_width=True)
            else:
                st.caption("No users have applied your codes yet.")
        else:
            st.caption("No code logs recorded yet.")
            
    else:
        st.info("Log in to create or view sale codes.")

# Auto-refresh trigger
st.fragment(run_every=30)(lambda: None)()
