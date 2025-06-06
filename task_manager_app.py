import streamlit as st
from datetime import datetime, date, timedelta

# Da die Kalender-Komponente Probleme macht, versuchen wir eine Alternative, falls die erste fehlschlägt.
# Zuerst versuchen wir die Standard-Bibliothek.
try:
    from streamlit_calendar import calendar
    CALENDAR_AVAILABLE = True
except ImportError:
    CALendar_AVAILABLE = False


# Seitenkonfiguration
st.set_page_config(layout="wide", page_title="Task Manager", page_icon="✅")

# --- Initialisierung des Session State mit Beispiel-Aufgaben ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {
            "id": "task_init_1",
            "title": "Wichtige Präsentation vorbereiten",
            "priority_level": 3,
            "priority_label": "Hoch",
            "completed": False,
            "deadline": date.today() + timedelta(days=4)
        },
        {
            "id": "task_init_2",
            "title": "Team-Meeting planen",
            "priority_level": 2,
            "priority_label": "Mittel",
            "completed": False,
            "deadline": None
        }
    ]

# --- Hilfsfunktionen ---
def get_task_index_by_id(task_id):
    for i, task in enumerate(st.session_state.tasks):
        if task['id'] == task_id:
            return i
    return None

def delete_task(task_id):
    task_index = get_task_index_by_id(task_id)
    if task_index is not None:
        st.session_state.tasks.pop(task_index)
        st.success("Aufgabe erfolgreich gelöscht!")
        st.rerun()

def format_deadline(deadline):
    if deadline:
        return f"Deadline: {deadline.strftime('%d.%m.%Y')}"
    return "Keine Deadline"

# --- HAUPT-UI (OHNE TABS) ---

st.title("✅ Task Manager")
st.markdown("---")

# --- TEIL 1: AUFGABEN ERSTELLEN UND ANZEIGEN ---
st.header("Aufgabenliste")

# Formular zum Erstellen
priorities = {"Niedrig": 1, "Mittel": 2, "Hoch": 3}
with st.form("new_task_form", clear_on_submit=True):
    new_task_title = st.text_input("Was ist zu tun?", placeholder="z.B. Meeting vorbereiten")
    col1, col2 = st.columns(2)
    with col1:
        new_task_priority_label = st.selectbox("Dringlichkeit:", options=priorities.keys())
    with col2:
        new_task_deadline = st.date_input("Deadline (optional):", value=None, min_value=datetime.today())
    submitted = st.form_submit_button("➕ Aufgabe hinzufügen")

    if submitted and new_task_title:
        new_task = {
            "id": f"task_{int(datetime.now().timestamp())}", "title": new_task_title,
            "priority_level": priorities[new_task_priority_label], "priority_label": new_task_priority_label,
            "completed": False, "deadline": new_task_deadline
        }
        st.session_state.tasks.append(new_task)
        st.success(f"Aufgabe '{new_task_title}' hinzugefügt!")
        st.rerun()

st.markdown("---")

# Anzeige der Aufgaben
if not st.session_state.tasks:
    st.info("Du hast derzeit keine Aufgaben.")
else:
    # Filter-Optionen
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_status = st.selectbox("Nach Status filtern:", ["Alle", "Offen", "Abgeschlossen"])
    with filter_col2:
        filter_priority = st.selectbox("Nach Dringlichkeit filtern:", ["Alle"] + list(priorities.keys()))

    # Logik zum Filtern und Sortieren
    filtered_tasks = [t for t in st.session_state.tasks if
                      (filter_status == "Alle" or (filter_status == "Offen" and not t['completed']) or (filter_status == "Abgeschlossen" and t['completed'])) and
                      (filter_priority == "Alle" or t['priority_label'] == filter_priority)]
    sorted_tasks = sorted(filtered_tasks, key=lambda x: (x['completed'], -x.get('priority_level', 0)))

    if not sorted_tasks:
        st.warning("Keine Aufgaben entsprechen deinen Filterkriterien.")
    else:
        for task in sorted_tasks:
            # (Der Code zur Anzeige der einzelnen Aufgaben bleibt unverändert)
            task_id, task_index = task['id'], get_task_index_by_id(task['id'])
            with st.container(border=True):
                col1, col2 = st.columns([0.05, 0.95])
                with col1:
                    is_completed = st.checkbox("", value=task['completed'], key=f"cb_{task_id}")
                    if is_completed != task['completed']:
                        st.session_state.tasks[task_index]['completed'] = is_completed
                        st.rerun()
                with col2:
                    title_display = f"**{task['title']}**"
                    if task['completed']: title_display = f"~~{title_display}~~"
                    with st.expander(f"{title_display} - Dringlichkeit: {task['priority_label']}"):
                        st.markdown(f"**{format_deadline(task.get('deadline'))}**")
                        st.markdown("---")
                        edited_title = st.text_input("Titel ändern:", value=task['title'], key=f"title_{task_id}")
                        edit_col1, edit_col2 = st.columns(2)
                        with edit_col1:
                            edited_priority = st.selectbox("Dringlichkeit ändern:", options=priorities.keys(), index=list(priorities.keys()).index(task['priority_label']), key=f"prio_{task_id}")
                        with edit_col2:
                            edited_deadline = st.date_input("Deadline ändern:", value=task.get('deadline'), key=f"deadline_{task_id}", min_value=datetime.today())
                        update_col, delete_col = st.columns([0.2, 0.8])
                        with update_col:
                           if st.button("💾 Speichern", key=f"save_{task_id}"):
                                st.session_state.tasks[task_index].update({
                                    'title': edited_title, 'priority_label': edited_priority,
                                    'priority_level': priorities[edited_priority], 'deadline': edited_deadline
                                })
                                st.rerun()
                        with delete_col:
                            if st.button("🗑️ Löschen", key=f"del_{task_id}", type="primary"):
                                delete_task(task_id)


# --- TEIL 2: KALENDERANSICHT ---
st.markdown("---")
st.header("🗓️ Kalenderansicht der Deadlines")

if not CALENDAR_AVAILABLE:
    st.error("Die Kalender-Bibliothek `streamlit-calendar` konnte nicht geladen werden. Bitte installiere sie mit `pip install streamlit-calendar`.")
else:
    # Konvertiere Tasks in das für die Kalender-Komponente benötigte Format
    calendar_events = []
    for task in st.session_state.tasks:
        if task.get("deadline"):
            color = "#3498DB"  # Blau für offen
            if task['completed']:
                color = "#2ECC71"  # Grün für abgeschlossen
            elif not task['completed'] and task['deadline'] < date.today():
                color = "#E74C3C"  # Rot für überfällig

            calendar_events.append({
                "title": task["title"], "start": task["deadline"].isoformat(),
                "end": task["deadline"].isoformat(), "color": color, "allDay": True,
            })

    # --- WICHTIGER DEBUGGING-SCHRITT ---
    st.markdown("Rohdaten für den Kalender (zum Debuggen):")
    st.json(calendar_events) # Diese Zeile zeigt die aufbereiteten Daten an.

    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridDay"},
        "initialView": "dayGridMonth", "locale": "de", "editable": False,
    }
    
    # Rendere den Kalender
    calendar(events=calendar_events, options=calendar_options, key=str(calendar_events)) # Key geändert für robustes Rerendering