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
status_filter = st.multiselect(
    "Filtr podle statusu", ["Čeká", "Schváleno", "Zamítnuto"], default=["Čeká", "Schváleno", "Zamítnuto"]
)
priorita_filter = st.multiselect(
    "Filtr podle priority", ["Vysoká", "Střední", "Nízká"], default=["Vysoká", "Střední", "Nízká"]
)
df_filtered = st.session_state.df[
    st.session_state.df["Status"].isin(status_filter) &
    st.session_state.df["Priorita"].isin(priorita_filter)
]

# --- Editace odvolání ---
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
        # Text columns are editable by default, no need to specify
    },
    disabled=["ID", "Hráč", "Důvod", "Datum"]
)

# --- Uložit změny ---
st.session_state.df.update(edited_df)
st.session_state.df.to_csv("odvolani.csv", index=False)

# --- Statistiky ---
st.header("Statistiky")
col1, col2, col3 = st.columns(3)
col1.metric("Čekající odvolání", len(st.session_state.df[st.session_state.df.Status=="Čeká"]))
col2.metric("Schválená odvolání", len(st.session_state.df[st.session_state.df.Status=="Schváleno"]))
col3.metric("Zamítnutá odvolání", len(st.session_state.df[st.session_state.df.Status=="Zamítnuto"]))

# --- Grafy ---
st.write("##### Status odvolání podle měsíce")
status_plot = (
    alt.Chart(edited_df)
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
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(
        theta="count():Q",
        color="Priorita:N"
    )
    .properties(height=300)
)
st.altair_chart(priority_plot, use_container_width=True)

