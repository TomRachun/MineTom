import os
import datetime
import pandas as pd
import streamlit as st
import altair as alt

# --- Nastavení stránky ---
st.set_page_config(page_title="Minecraft vězeňské odvolání", page_icon="⛏️")
st.title("⛏️ Minecraft vězeňské odvolání")
st.write("Zde můžeš podat odvolání, pokud jsi byl uvězněn. Vysvětli, proč bys neměl být ve vězení.")

# --- Načtení dat ---
if os.path.exists("odvolani.csv"):
    st.session_state.df = pd.read_csv("odvolani.csv")
else:
    st.session_state.df = pd.DataFrame(
        columns=["ID", "Hráč", "Důvod", "Status", "Priorita", "Datum", "Komentář"]
    )

# --- Admin login ---
st.sidebar.header("Admin přístup")
admin_password = "minecraft123"  # nastavte své heslo
admin_mode = st.sidebar.checkbox("Admin režim")
if admin_mode:
    password_input = st.sidebar.text_input("Zadej admin heslo", type="password")
    if password_input != admin_password:
        st.sidebar.error("Špatné heslo!")
        admin_mode = False
    else:
        st.sidebar.success("Admin režim aktivní ✅")

# --- Nové odvolání ---
st.header("Podat nové odvolání")
with st.form("form_odvolani"):
    hrac = st.text_input("Minecraft uživatelské jméno")
    duvod = st.text_area("Proč bys měl být propuštěn?")
    priorita = st.selectbox("Priorita odvolání", ["Vysoká", "Střední", "Nízká"])
    submit = st.form_submit_button("Odeslat odvolání")

if submit:
    new_id = (
        int(st.session_state.df["ID"].str.split("-").str[1].max()) + 1
        if not st.session_state.df.empty else 1001
    )
    dnes = datetime.datetime.now().strftime("%Y-%m-%d")
    new_row = pd.DataFrame([{
        "ID": f"ODVOLANI-{new_id}",
        "Hráč": hrac,
        "Důvod": duvod,
        "Status": "Čeká",
        "Priorita": priorita,
        "Datum": dnes,
        "Komentář": ""
    }])
    st.session_state.df = pd.concat([new_row, st.session_state.df], axis=0)
    st.success("Odvolání bylo odesláno!")
    st.session_state.df.to_csv("odvolani.csv", index=False)

# --- Filtry ---
st.header("Správa odvolání")
if admin_mode:
    # Admin vidí všechna odvolání
    df_filtered = st.session_state.df.copy()
else:
    # Hráči vidí jen svá odvolání
    hrac_input = st.text_input("Zadej své Minecraft jméno pro zobrazení odvolání")
    if hrac_input:
        df_filtered = st.session_state.df[st.session_state.df["Hráč"] == hrac_input]
    else:
        df_filtered = pd.DataFrame(columns=st.session_state.df.columns)

status_filter = st.multiselect(
    "Filtr podle statusu",
    ["Čeká", "Schváleno", "Zamítnuto"],
    default=["Čeká", "Schváleno", "Zamítnuto"] if admin_mode else ["Čeká", "Schváleno", "Zamítnuto"]
)
priorita_filter = st.multiselect(
    "Filtr podle priority",
    ["Vysoká", "Střední", "Nízká"],
    default=["Vysoká", "Střední", "Nízká"]
)
df_filtered = df_filtered[
    df_filtered["Status"].isin(status_filter) &
    df_filtered["Priorita"].isin(priorita_filter)
]

# --- Editace odvolání ---
st.subheader("Úpravy odvolání")
if admin_mode:
    edited_df = st.data_editor(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status", options=["Čeká", "Schváleno", "Zamítnuto"], required=True
            ),
            "Priorita": st.column_config.SelectboxColumn(
                "Priorita", options=["Vysoká", "Střední", "Nízká"], required=True
            ),
        },
        disabled=["ID", "Hráč", "Důvod", "Datum"]
    )
    # Uložit změny
    st.session_state.df.update(edited_df)
    st.session_state.df.to_csv("odvolani.csv", index=False)

# --- Smazání odvolání (jen admin) ---
if admin_mode:
    st.subheader("Smazání odvolání")
    delete_ids = []
    for i, row in st.session_state.df.iterrows():
        if st.checkbox(f"Smazat {row['ID']} - {row['Hráč']}", key=f"del_{row['ID']}"):
            delete_ids.append(i)
    if delete_ids and st.button("Smazat vybraná odvolání"):
        st.session_state.df.drop(delete_ids, inplace=True)
        st.session_state.df.to_csv("odvolani.csv", index=False)
        st.success(f"Smazáno {len(delete_ids)} odvolání!")

# --- Statistiky ---
st.header("Statistiky")
col1, col2, col3 = st.columns(3)
col1.metric("Čekající odvolání", len(st.session_state.df[st.session_state.df.Status=="Čeká"]))
col2.metric("Schválená odvolání", len(st.session_state.df[st.session_state.df.Status=="Schváleno"]))
col3.metric("Zamítnutá odvolání", len(st.session_state.df[st.session_state.df.Status=="Zamítnuto"]))

# --- Grafy ---
st.write("##### Status odvolání podle měsíce")
if not df_filtered.empty:
    status_plot = (
        alt.Chart(df_filtered)
        .mark_bar()
        .encode(
            x=alt.X("month(Datum):O", title="Měsíc"),
            y=alt.Y("count():Q", title="Počet odvolání"),
            xOffset="Status:N",
            color="Status:N"
        )
    )
    st.altair_chart(status_plot, use_container_width=True)

st.write("##### Priority odvolání")
if not df_filtered.empty:
    priority_plot = (
        alt.Chart(df_filtered)
        .mark_arc()
        .encode(
            theta="count():Q",
            color="Priorita:N"
        )
        .properties(height=300)
    )
    st.altair_chart(priority_plot, use_container_width=True)

