import os
import datetime
import pandas as pd
import streamlit as st

# ─── CONFIG ──────────────────────────────────────────────
st.set_page_config(page_title="Minecraft vězení & odvolání", page_icon="⛓️")
st.title("⛓️ Minecraft vězení & odvolání")

DATA_FILE = "odvolani.csv"
ADMIN_PASSWORD = "minecraft123"

COLUMNS = [
    "ID", "Hráč",
    "Důvod_trestu",
    "Celkem_dní",
    "Odslouženo",
    "Datum_trestu",
    "Status_trestu",
    "Odvolání",
    "Status_odvolání",
    "Komentář_admina"
]

# ─── LOAD DATA ───────────────────────────────────────────
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=COLUMNS)
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
st.header("🔍 Stav trestu")

player_name = st.text_input("Minecraft jméno")

if player_name:
    now = datetime.datetime.now()
    p_df = st.session_state.df[
        st.session_state.df["Hráč"].str.lower() == player_name.lower()
    ]

    if p_df.empty:
        st.info("Žádný aktivní trest.")
    else:
        rows = []
        for _, r in p_df.iterrows():
            created = datetime.datetime.fromisoformat(r["Datum_trestu"])
            days_passed = (now - created).days
            served = int(r["Odslouženo"]) + days_passed

            if int(r["Celkem_dní"]) == 0:
                remaining = "PERMANENT"
            else:
                remaining = max(0, int(r["Celkem_dní"]) - served)

            rows.append({
                "Důvod trestu": r["Důvod_trestu"],
                "Zbývá": remaining,
                "Status": r["Status_trestu"],
                "Odvolání": r["Status_odvolání"]
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        # ─── APPEAL FORM ──────────────────────────────────
        st.subheader("📨 Podat odvolání")
        with st.form("appeal_form"):
            appeal_text = st.text_area("Napiš odvolání")
            send = st.form_submit_button("Odeslat")

        if send and appeal_text:
            idx = p_df.index[0]
            st.session_state.df.at[idx, "Odvolání"] = appeal_text
            st.session_state.df.at[idx, "Status_odvolání"] = "Čeká"
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("Odvolání odesláno")

# ─── ADMIN PANEL ─────────────────────────────────────────
if admin_mode:
    st.divider()
    st.header("🛠️ Admin panel")

    # ADD JAIL CASE
    with st.form("add_case"):
        st.subheader("Přidat trest")
        hrac = st.text_input("Hráč")
        duvod = st.text_input("Důvod trestu")
        total = st.number_input("Délka (0 = PERMA)", min_value=0, step=1)
        submit = st.form_submit_button("Přidat")

        if submit and hrac and duvod:
            new_id = (
                st.session_state.df["ID"].max() + 1
                if not st.session_state.df.empty else 1
            )
            row = {
                "ID": int(new_id),
                "Hráč": hrac,
                "Důvod_trestu": duvod,
                "Celkem_dní": int(total),
                "Odslouženo": 0,
                "Datum_trestu": datetime.datetime.now().isoformat(),
                "Status_trestu": "Aktivní",
                "Odvolání": "",
                "Status_odvolání": "",
                "Komentář_admina": ""
            }
            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([row])],
                ignore_index=True
            )
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("Trest přidán")

    # EDIT CASES + APPEALS
    if not st.session_state.df.empty:
        st.subheader("Úpravy trestů a odvolání")

        edited = st.data_editor(
            st.session_state.df,
            disabled=["ID", "Hráč", "Datum_trestu"],
            column_config={
                "Status_trestu": st.column_config.SelectboxColumn(
                    "Status trestu",
                    options=["Aktivní", "Ukončen"]
                ),
                "Status_odvolání": st.column_config.SelectboxColumn(
                    "Status odvolání",
                    options=["", "Čeká", "Schváleno", "Zamítnuto"]
                )
            },
            use_container_width=True
        )

        if st.button("Uložit změny"):
            st.session_state.df = edited
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("Uloženo")

        # DELETE
        st.subheader("Smazat trest")
        del_id = st.selectbox("Vyber ID", st.session_state.df["ID"])
        if st.button("Smazat"):
            st.session_state.df = st.session_state.df[
                st.session_state.df["ID"] != del_id
            ]
            st.session_state.df.to_csv(DATA_FILE, index=False)
            st.success("Smazáno")



