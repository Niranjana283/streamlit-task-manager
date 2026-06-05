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
html = "<div style='overflow-x:auto; margin-top: 10px; padding-bottom: 10px;'>"
html += "<table style='width:100%; border-collapse:collapse; text-align:left; min-width: 800px;'>"
html += "<thead><tr style='border-bottom:1px solid #21262d;'>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>👤 User</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>📌 Main Task</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>📝 Sub Task</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>🔥 Priority</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>📅 Start</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>📅 End</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>Status</th>"
html += "</tr></thead><tbody>"

filtered = 0
for row in all_tasks:
    name, main, sub, prio, start, end, done = row
    status = "Completed" if done == 1 else "Pending"

    if status_filter != "All" and status_filter != status:
        continue

    filtered += 1
    pcolor = PRIORITY_COLOR.get(prio, "#8b949e")
    scolor = "#3fb950" if done == 1 else "#d29922"

    html += "<tr style='border-bottom:1px solid #21262d;'>"
    html += f"<td style='padding:12px 8px; color:#c9d1d9; font-weight:600;'>{name}</td>"
    html += f"<td style='padding:12px 8px; color:#e6edf3;'>{main or '—'}</td>"
    html += f"<td style='padding:12px 8px; color:#8b949e;'>{sub or '—'}</td>"
    html += f"<td style='padding:12px 8px;'>{badge(prio or '—', pcolor)}</td>"
    html += f"<td style='padding:12px 8px; color:#8b949e; font-size:.85rem;'>{start or '—'}</td>"
    html += f"<td style='padding:12px 8px; color:#8b949e; font-size:.85rem;'>{end or '—'}</td>"
    html += f"<td style='padding:12px 8px;'>{badge(status, scolor)}</td>"
    html += "</tr>"

html += "</tbody></table></div>"
if filtered > 0:
    st.markdown(html, unsafe_allow_html=True)

if filtered == 0:
    st.info("No tasks match the selected filters.")