import streamlit as st
from database import cursor
from auth_guard import require_login, get_user
from theme import inject_theme, page_header, section_header, badge, PRIORITY_COLOR

st.set_page_config(page_title="All Tasks · TaskFlow", page_icon="📂", layout="wide", initial_sidebar_state="expanded")
inject_theme()
require_login()
user = get_user()

page_header("📂", "All Tasks", "View and filter tasks across all team members")

# ── Filters ──
section_header("Filters")

users    = cursor.execute("SELECT name FROM users").fetchall()
user_list = [u[0] for u in users]

col1, col2, col3 = st.columns(3)
user_filter   = col1.selectbox("👤 User",     ["All Users"] + user_list)
status_filter = col2.selectbox("📌 Status",   ["All", "Completed", "Pending"])
prio_filter   = col3.selectbox("🔥 Priority", ["All", "High", "Medium", "Low"])

# ── Query ──
query  = """
SELECT users.name, tasks.main_task, tasks.sub_task,
       tasks.priority, tasks.due_date, tasks.end_date, tasks.completed
FROM tasks JOIN users ON tasks.user_id = users.id
WHERE tasks.sub_task IS NOT NULL
"""
params = []
if user_filter != "All Users":
    query += " AND users.name=?"
    params.append(user_filter)
if prio_filter != "All":
    query += " AND tasks.priority=?"
    params.append(prio_filter)

query += " ORDER BY tasks.due_date DESC"
all_tasks = cursor.execute(query, params).fetchall()

# ── Stats banner ──
st.markdown("<br>", unsafe_allow_html=True)

total     = len(all_tasks)
completed = sum(1 for t in all_tasks if t[6] == 1)
pending   = total - completed

s1, s2, s3 = st.columns(3)
def stat_card(icon, label, value, color):
    return (f"<div style='background:#161b22;border:1px solid #30363d;"
            f"border-left:4px solid {color};border-radius:12px;padding:16px 20px;'>"
            f"<p style='color:#8b949e;font-size:.75rem;text-transform:uppercase;"
            f"letter-spacing:1px;margin:0 0 6px;'>{icon} {label}</p>"
            f"<p style='color:#e6edf3;font-size:1.8rem;font-weight:800;margin:0;'>{value}</p></div>")

s1.markdown(stat_card("📋","Total",    total,     "#58a6ff"), unsafe_allow_html=True)
s2.markdown(stat_card("✅","Completed",completed, "#3fb950"), unsafe_allow_html=True)
s3.markdown(stat_card("⏳","Pending",  pending,   "#d29922"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
section_header("Task List")

if not all_tasks:
    st.info("No tasks match the selected filters.")
    st.stop()

# Table header
h1,h2,h3,h4,h5,h6,h7 = st.columns([1.6,2.2,2.2,1.2,1.4,1.4,1.4])
for col, label in zip([h1,h2,h3,h4,h5,h6,h7],
    ["👤 User","📌 Main Task","📝 Sub Task","🔥 Priority","📅 Start","📅 End","Status"]):
    col.markdown(f"<p style='color:#8b949e;font-size:.72rem;font-weight:600;"
                 f"text-transform:uppercase;letter-spacing:.7px;margin:0;'>{label}</p>",
                 unsafe_allow_html=True)

st.markdown("<hr style='margin:8px 0 4px;border-color:#21262d;'>", unsafe_allow_html=True)

filtered = 0
for row in all_tasks:
    name, main, sub, prio, start, end, done = row
    status = "Completed" if done == 1 else "Pending"

    if status_filter != "All" and status_filter != status:
        continue

    filtered += 1
    pcolor = PRIORITY_COLOR.get(prio, "#8b949e")
    scolor = "#3fb950" if done == 1 else "#d29922"

    c1,c2,c3,c4,c5,c6,c7 = st.columns([1.6,2.2,2.2,1.2,1.4,1.4,1.4])
    c1.markdown(f"<span style='color:#c9d1d9;font-weight:600;'>{name}</span>", unsafe_allow_html=True)
    c2.markdown(f"<span style='color:#e6edf3;'>{main or '—'}</span>", unsafe_allow_html=True)
    c3.markdown(f"<span style='color:#8b949e;'>{sub or '—'}</span>", unsafe_allow_html=True)
    c4.markdown(badge(prio or "—", pcolor), unsafe_allow_html=True)
    c5.markdown(f"<span style='color:#8b949e;font-size:.85rem;'>{start or '—'}</span>", unsafe_allow_html=True)
    c6.markdown(f"<span style='color:#8b949e;font-size:.85rem;'>{end or '—'}</span>", unsafe_allow_html=True)
    c7.markdown(badge(status, scolor), unsafe_allow_html=True)

    st.markdown("<hr style='margin:4px 0;border-color:#21262d;'>", unsafe_allow_html=True)

if filtered == 0:
    st.info("No tasks match the selected filters.")