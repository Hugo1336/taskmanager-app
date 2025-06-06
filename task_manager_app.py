import streamlit as st
import pandas as pd
from datetime import datetime

DATA_FILE = "tasks.csv"  # Alternativ: "tasks.tsv" mit sep="\t"

# Daten laden oder neue Tabelle anlegen
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        df["Deadline"] = pd.to_datetime(df["Deadline"], errors='coerce')
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Title", "Assignees", "Status", "Priority", "Estimate", "Size", "Deadline"])
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# App-Start
st.title("🗂️ Task Manager App")

df = load_data()

# --- NEUE AUFGABE HINZUFÜGEN ---
with st.expander("➕ Neue Aufgabe hinzufügen"):
    with st.form("add_task"):
        title = st.text_input("Titel", "")
        assignees = st.text_input("Zuständig")
        status = st.selectbox("Status", ["Todo", "In Progress", "Done"])
        priority = st.selectbox("Priorität", ["P0", "P1", "P2"])
        estimate = st.number_input("Aufwand (Stunden)", min_value=0.0, value=1.0)
        size = st.selectbox("Größe", ["XS", "S", "M", "L", "XL"])
        deadline = st.date_input("Deadline", value=None)
        submitted = st.form_submit_button("Aufgabe hinzufügen")
        if submitted and title:
            new_row = pd.DataFrame([{
                "Title": title,
                "Assignees": assignees,
                "Status": status,
                "Priority": priority,
                "Estimate": estimate,
                "Size": size,
                "Deadline": deadline
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Aufgabe hinzugefügt!")

# --- FILTER UND ÜBERSICHT ---
status_options = df["Status"].dropna().unique().tolist()
default_status = [s for s in ["Todo", "In Progress"] if s in status_options]
status_filter = st.multiselect("Status-Filter", options=status_options, default=default_status)
filtered = df[df["Status"].isin(status_filter)]

st.subheader("📋 Offene Aufgaben")
st.dataframe(filtered)

# --- KALENDERANSICHT ---

import streamlit_calendar as st_calen

st.subheader("📋 Offene Aufgaben")
st.dataframe(filtered)

st.subheader("📅 Kalenderansicht der Aufgaben")
calendar_events = []
for _, row in filtered.iterrows():
    if pd.notna(row["Deadline"]):
        calendar_events.append({
            "title": row["Title"],
            "start": row["Deadline"].strftime("%Y-%m-%d"),
            "end": row["Deadline"].strftime("%Y-%m-%d"),
            "allDay": True,
        })

calendar_options = {
    "initialView": "dayGridMonth",
    "locale": "de",
    "height": 500,
}

st_calen.calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css="""
        .fc-event-title { font-size: 1rem; }
    """
)

# --- AUFGABEN BEARBEITEN UND LÖSCHEN ---
st.subheader("✏️ Aufgabe bearbeiten oder löschen")
for idx, row in filtered.iterrows():
    with st.expander(f"🔹 {row['Title']}"):
        col1, col2 = st.columns(2)
        with col1:
            new_status = st.selectbox("Status", ["Todo", "In Progress", "Done"], index=["Todo", "In Progress", "Done"].index(row["Status"]), key=f"status_{idx}")
            new_deadline = st.date_input("Deadline", value=row["Deadline"] if pd.notna(row["Deadline"]) else datetime.today(), key=f"deadline_{idx}")
        with col2:
            if st.button("✅ Speichern", key=f"save_{idx}"):
                df.at[idx, "Status"] = new_status
                df.at[idx, "Deadline"] = new_deadline
                save_data(df)
                st.success("Aufgabe aktualisiert.")
                st.experimental_rerun()

            if st.button("🗑️ Löschen", key=f"delete_{idx}"):
                df = df.drop(index=idx).reset_index(drop=True)
                save_data(df)
                st.warning("Aufgabe gelöscht.")
                st.experimental_rerun()

