import streamlit as st
from database import cursor, conn
from datetime import datetime, timedelta
from auth_guard import require_login, get_user
from theme import inject_theme, page_header, section_header, badge, PRIORITY_COLOR

st.set_page_config(page_title="Task Management · TaskFlow", page_icon="📋", layout="wide", initial_sidebar_state="expanded")
inject_theme()
require_login()
user = get_user()

page_header("📋", "Task Management", "Create weekly tasks and log daily activities")

is_admin = user["role"] == "admin"

def validate_time(t):
    try:
        datetime.strptime(t, "%H:%M")
        return True
    except:
        return False

# ── User selector ──
all_users = cursor.execute("SELECT id, name FROM users").fetchall()
if not all_users:
    st.warning("No users found. Please create a user first.")
    st.stop()

user_dict = {u[1]: u[0] for u in all_users}

if is_admin:
    selected_user = st.selectbox("👤 Select User", list(user_dict.keys()))
else:
    own_name  = user["username"]
    all_names = list(user_dict.keys())
    selected_user = st.selectbox(
        "👤 Select User", all_names,
        index=all_names.index(own_name) if own_name in all_names else 0,
    )
    if selected_user != own_name:
        st.error("🚫 You don't have permission to access other users' tasks. Only admins can do that.")
        st.stop()

user_id = user_dict[selected_user]

st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# 1️⃣ CREATE MAIN TASK
# ======================================================
section_header("Create Weekly Main Task")

with st.form("main_task_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    main_task  = col_a.text_input("Main Task", placeholder="e.g. Website Redesign")
    priority   = col_b.selectbox("Priority", ["High", "Medium", "Low"])
    col_c, col_d = st.columns(2)
    start_date = col_c.date_input("Start Date")
    end_date   = col_d.date_input("End Date")
    submit_main = st.form_submit_button("📌 Create Main Task", use_container_width=True)

if submit_main:
    if not main_task.strip():
        st.error("Main task name cannot be empty.")
    elif start_date > end_date:
        st.error("Start date cannot be after end date.")
    else:
        cursor.execute(
            "INSERT INTO tasks (user_id, main_task, priority, start_date, end_date, completed) VALUES (?,?,?,?,?,0)",
            (user_id, main_task.strip(), priority, str(start_date), str(end_date))
        )
        conn.commit()
        st.success(f"✅ Main task **{main_task}** created!")
        st.rerun()

# ======================================================
# 2️⃣ SELECT MAIN TASK
# ======================================================
main_tasks = cursor.execute(
    "SELECT DISTINCT main_task, priority FROM tasks WHERE user_id=? AND main_task IS NOT NULL",
    (user_id,)
).fetchall()

if not main_tasks:
    st.info("No main tasks yet. Create one above to get started.")
    st.stop()

# Show main tasks as selectable cards
section_header("Select Main Task")
task_names = [m[0] for m in main_tasks]
task_prio  = {m[0]: m[1] for m in main_tasks}

selected_main_task = st.selectbox("📌 Active Task", task_names, label_visibility="collapsed")

pcolor = PRIORITY_COLOR.get(task_prio.get(selected_main_task, "Low"), "#8b949e")
st.markdown(
    f"<div style='background:#161b22;border:1px solid #30363d;border-left:4px solid {pcolor};"
    f"border-radius:10px;padding:14px 18px;display:flex;align-items:center;gap:12px;margin-bottom:8px;'>"
    f"<span style='font-size:1.4rem;'>📌</span>"
    f"<div><p style='color:#e6edf3;font-weight:700;margin:0;'>{selected_main_task}</p>"
    f"<p style='margin:4px 0 0;'>{badge(task_prio.get(selected_main_task,'—'), pcolor)}</p></div></div>",
    unsafe_allow_html=True
)

# ======================================================
# 3️⃣ ADD DAILY ACTIVITY
# ======================================================
section_header("Add Daily Activity")

with st.form("sub_task_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    activity_date = col1.date_input("Activity Date")
    sub_task      = col2.text_input("Daily Activity", placeholder="e.g. UI wireframing")

    col3, col4, col5 = st.columns(3)
    time_in      = col3.text_input("Time In (HH:MM)",  placeholder="09:00")
    time_out     = col4.text_input("Time Out (HH:MM)", placeholder="18:00")
    leave_reason = col5.text_input("Leave Reason", placeholder="Optional")

    submit_sub = st.form_submit_button("➕ Add Activity", use_container_width=True)

if submit_sub:
    if not sub_task.strip() and not leave_reason.strip():
        st.error("Enter an activity description or leave reason.")
    elif time_in and time_out and (not validate_time(time_in) or not validate_time(time_out)):
        st.error("❌ Enter times in HH:MM format (e.g. 09:00).")
    else:
        if leave_reason.strip():
            sub_task = "Leave"
        cursor.execute(
            "INSERT INTO tasks (user_id, main_task, sub_task, due_date, time_in, time_out, leave_reason, completed) VALUES (?,?,?,?,?,?,?,0)",
            (user_id, selected_main_task, sub_task, str(activity_date), time_in, time_out, leave_reason)
        )
        conn.commit()
        st.success("✅ Activity logged!")
        st.rerun()

# ======================================================
# 4️⃣ ACTIVITIES LIST
# ======================================================
section_header("Activity Log")

activities = cursor.execute(
    "SELECT id, sub_task, due_date, completed, time_in, time_out, leave_reason FROM tasks "
    "WHERE user_id=? AND main_task=? AND sub_task IS NOT NULL ORDER BY due_date",
    (user_id, selected_main_task)
).fetchall()

if not activities:
    st.info("No activities logged yet for this task.")
else:
    for act in activities:
        act_id, sub, due, done, tin, tout, leave = act

        # Duration calc
        dur_text = ""
        if tin and tout:
            try:
                t1 = datetime.strptime(tin, "%H:%M")
                t2 = datetime.strptime(tout, "%H:%M")
                dur = (t2 + timedelta(days=1)) - t1 if t2 < t1 else t2 - t1
                dur_text = f" · ⏱ {str(dur)[:-3]}"
            except:
                pass

        leave_text = f" · 🏖 {leave}" if leave else ""
        time_text  = f"⏰ {tin}–{tout}" if tin and tout else ""
        status_color = "#3fb950" if done else "#d29922"
        status_label = "Completed" if done else "Pending"

        c1, c2, c3, c4 = st.columns([7, 1, 1, 1])

        task_html = (
            f"<span style='color:#8b949e;font-size:.78rem;'>📅 {due}</span> "
            f"<span style='color:{'#6e7681' if done else '#e6edf3'};font-weight:600;"
            f"{'text-decoration:line-through;' if done else ''}'> {sub}</span> "
            f"<span style='color:#8b949e;font-size:.8rem;'>{time_text}{dur_text}{leave_text}</span> "
            f"{badge(status_label, status_color)}"
        )
        c1.markdown(task_html, unsafe_allow_html=True)

        if c2.button("✅", key=f"complete_{act_id}", help="Mark complete"):
            cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (act_id,))
            conn.commit(); st.rerun()

        if c3.button("✏️", key=f"edit_{act_id}", help="Edit"):
            st.session_state[f"editing_{act_id}"] = True

        if c4.button("🗑", key=f"del_{act_id}", help="Delete"):
            cursor.execute("DELETE FROM tasks WHERE id=?", (act_id,))
            conn.commit(); st.rerun()

        if st.session_state.get(f"editing_{act_id}"):
            with st.form(key=f"edit_form_{act_id}"):
                ea, eb, ec = st.columns(3)
                new_text  = ea.text_input("Activity", value=sub,    key=f"et_{act_id}")
                new_tin   = eb.text_input("Time In",  value=tin or "", key=f"ti_{act_id}")
                new_tout  = ec.text_input("Time Out", value=tout or "", key=f"to_{act_id}")
                new_leave = st.text_input("Leave Reason", value=leave or "", key=f"lv_{act_id}")
                sv, cx = st.columns(2)
                save   = sv.form_submit_button("💾 Save")
                cancel = cx.form_submit_button("Cancel")
            if save:
                if new_tin and new_tout and (not validate_time(new_tin) or not validate_time(new_tout)):
                    st.error("Invalid time format.")
                else:
                    cursor.execute(
                        "UPDATE tasks SET sub_task=?, time_in=?, time_out=?, leave_reason=? WHERE id=?",
                        (new_text, new_tin, new_tout, new_leave, act_id)
                    )
                    conn.commit()
                    st.session_state[f"editing_{act_id}"] = False
                    st.rerun()
            if cancel:
                st.session_state[f"editing_{act_id}"] = False
                st.rerun()

        st.markdown("<hr style='margin:4px 0;border-color:#21262d;'>", unsafe_allow_html=True)