import os
import datetime
import pandas as pd
import streamlit as st

# ─── PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(page_title="Minecraft vězení", page_icon="⛓️")
st.title("⛓️ Minecraft vězeňský systém")

DATA_FILE = "odvolani.csv"
ADMIN_PASSWORD = "minecraft123"

# ─── LOAD / INIT DATA ────────────────────────────────────
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "ID", "Hráč", "Důvod",
        "Celkem_dní", "Odslouženo",
        "Datum", "Status"
    ])
    df.to_csv(DATA_FILE, index=False)

st.session_state.df = df

# ─── ADMIN LOGIN ─────────────────────────────────────────
st.sidebar.header("Admin")
admin_mode = st.sidebar.checkbox("Admin režim")

if admin_mode:
    pw = st.sidebar.text_input("Heslo", type="password")
    if pw != ADMIN_PASSWORD:
        st.sidebar.error("Špatné heslo")
        admin_mode = False
    else:
        st.sidebar.success("Admin aktivní")

# ─── PLAYER VIEW ─────────────────────────────────────────
st.header("🔍 Zkontroluj svůj trest")

player_name = st.text_input("Minecraft jméno")

if player_name:
    now = datetime.datetime.now()
    player_df = st.session_state.df[
        st.session_state.df["Hráč"].str.lower() == player_name.lower()
    ]

    if not player_df.empty:
        rows = []
        for _, r in player_df.iterrows():
            created = datetime.datetime.fromisoformat(r["Datum"])
            days_passed = (now - created).days
            served = int(r["Odslouženo"]) + days_passed

            if int(r["Celkem_dní"]) == 0:
                remaining = "PERMANENT"
            else:
                remaining = max(0, int(r["Celkem_dní"]) - served)

            rows.append({
                "Důvod": r["Důvod"],
                "Celkem dní": "PERMA" if r["Celkem_dní"] == 0 else r["Celkem_dní"],
                "Odslouženo (≈)": served,
                "Zbývá": remaining,
                "Status": r["Status"]
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("Žádný trest nenalezen.")

# ─── ADMIN PANEL ─────────────────────────────────────────
if admin_mode:
    st.divider()
    st.header("🛠️ Správa vězení (admin)")

    # ADD CASE
    with st.form("add_case"):
        st.subheader("Přidat trest")
        hrac = st.text_input("Hráč")
        duvod = st.text_input("Důvod")
        total_days = st.number_input("Délka trestu (0 = PERMA)", min_value=0, step=1)
        submit = st.form_submit_button("Přidat")

        if submit and hrac and duvod:
            new_id = (
                st.session_state.df["ID"].max() + 1
                if not st.session_state.df.empty else 1
            )
            new_row = {
                "ID": int(new_id),
                "Hráč": hrac,
                "Důvod": duvod,
                "Celkem_dní": int(total_days),
                "Odslouženo": 0,
                "Datum": datetime.datetime.now().isoformat(),
                "Status": "Aktivní"
            }
            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("Trest přidán")

    # EDIT CASES
    if not st.session_state.df.empty:
        st.subheader("Upravit tresty")

        edited_df = st.data_editor(
            st.session_state.df,
            disabled=["ID", "Hráč", "Důvod", "Datum"],
            use_container_width=True
        )

        if st.button("Uložit změny"):
            st.session_state.df = edited_df
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("Změny uloženy")

        # DELETE
        st.subheader("Smazat trest")
        delete_id = st.selectbox(
            "Vyber ID",
            st.session_state.df["ID"]
        )

        if st.button("Smazat"):
            st.session_state.df = st.session_state.df[
                st.session_state.df["ID"] != delete_id
            ]
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("Trest smazán")


