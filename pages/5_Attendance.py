import streamlit as st
from database import cursor
import pandas as pd
from io import BytesIO
from datetime import datetime
from auth_guard import require_login, get_user
from theme import inject_theme, page_header, section_header, badge, STATUS_COLOR

st.set_page_config(page_title="Attendance · TaskFlow", page_icon="🗓️", layout="wide", initial_sidebar_state="expanded")
inject_theme()
require_login()
user = get_user()

page_header("🗓️", "Attendance", "Track and review daily check-in / check-out records")

# ── Holidays ──
HOLIDAYS = ["2026-01-26", "2026-08-15", "2026-10-02"]

# ── Filters ──
users     = cursor.execute("SELECT id, name FROM users").fetchall()
user_dict = {u[1]: u[0] for u in users}

st.sidebar.markdown("### 🔍 Filters")
selected_user = st.sidebar.selectbox("👤 Filter by User", ["All"] + list(user_dict.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("**📅 Date Range**")
from_date = st.sidebar.date_input("From Date", pd.to_datetime("today").date() - pd.Timedelta(days=30))
to_date   = st.sidebar.date_input("To Date", pd.to_datetime("today").date())

# ── Fetch ──
if selected_user == "All":
    records = cursor.execute("""
        SELECT u.name, t.due_date, t.time_in, t.time_out, t.leave_reason
        FROM tasks t JOIN users u ON t.user_id = u.id
        WHERE t.sub_task IS NOT NULL AND t.due_date BETWEEN ? AND ? ORDER BY t.due_date DESC
    """, (str(from_date), str(to_date))).fetchall()
else:
    uid = user_dict[selected_user]
    records = cursor.execute("""
        SELECT u.name, t.due_date, t.time_in, t.time_out, t.leave_reason
        FROM tasks t JOIN users u ON t.user_id = u.id
        WHERE t.user_id=? AND t.sub_task IS NOT NULL AND t.due_date BETWEEN ? AND ? ORDER BY t.due_date DESC
    """, (uid, str(from_date), str(to_date))).fetchall()

if not records:
    st.info("No attendance records found.")
    st.stop()

# ── Status resolver ──
def resolve_status(date_str, time_in, time_out, leave_reason):
    try:
        date_obj   = datetime.strptime(date_str, "%Y-%m-%d")
        is_weekend = date_obj.weekday() >= 5
        is_holiday = date_str in HOLIDAYS
        day_name   = date_obj.strftime("%A")
    except:
        return "—", "—", "#8b949e"

    if is_weekend or is_holiday:
        return day_name, "Not Working Day", STATUS_COLOR["Not Working Day"]
    elif leave_reason:
        return day_name, "Leave", STATUS_COLOR["Leave"]
    elif time_in and time_out:
        return day_name, "Present", STATUS_COLOR["Present"]
    else:
        return day_name, "Partial", STATUS_COLOR["Partial"]

# ── Live KPI banner ──
st.markdown("<br>", unsafe_allow_html=True)
section_header("Attendance Summary")

present_count = 0
leave_count   = 0
partial_count = 0
off_count     = 0
for r in records:
    _, status, _ = resolve_status(r[1], r[2], r[3], r[4])
    if status == "Present":       present_count += 1
    elif status == "Leave":       leave_count   += 1
    elif status == "Partial":     partial_count += 1
    elif status == "Not Working Day": off_count += 1

k1, k2, k3, k4 = st.columns(4)
def kpi(icon, label, value, color):
    return (f"<div style='background:#161b22;border:1px solid #30363d;"
            f"border-left:4px solid {color};border-radius:12px;padding:18px 20px;'>"
            f"<p style='color:#8b949e;font-size:.72rem;text-transform:uppercase;"
            f"letter-spacing:1px;margin:0 0 8px;'>{icon} {label}</p>"
            f"<p style='color:#e6edf3;font-size:1.8rem;font-weight:800;margin:0;'>{value}</p></div>")

k1.markdown(kpi("✅","Present",        present_count, "#3fb950"), unsafe_allow_html=True)
k2.markdown(kpi("❌","On Leave",       leave_count,   "#f85149"), unsafe_allow_html=True)
k3.markdown(kpi("⚠️","Partial",        partial_count, "#d29922"), unsafe_allow_html=True)
k4.markdown(kpi("🟡","Non-Working",    off_count,     "#8b949e"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
section_header("Records")

# ── TABLE VIEW ──
html = "<div style='overflow-x:auto; margin-top: 10px; padding-bottom: 10px;'>"
html += "<table style='width:100%; border-collapse:collapse; text-align:left; min-width: 800px;'>"
html += "<thead><tr style='border-bottom:1px solid #21262d;'>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>👤 User</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>📅 Date</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>📆 Day</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>🟢 In</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>🔴 Out</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>⏱ Duration</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>📌 Status</th>"
html += "<th style='padding:8px 8px 12px 8px; color:#8b949e; font-size:.72rem; text-transform:uppercase; letter-spacing:.7px; font-weight:600;'>🏖️ Reason</th>"
html += "</tr></thead><tbody>"

for r in records:
    name, date, time_in, time_out, leave_reason = r
    day_name, status, color = resolve_status(date, time_in, time_out, leave_reason)

    dur_text = "—"
    if time_in and time_out:
        try:
            t1  = datetime.strptime(time_in,  "%H:%M")
            t2  = datetime.strptime(time_out, "%H:%M")
            dur = (t2 - t1).seconds // 60
            dur_text = f"{dur//60}h {dur%60}m"
        except:
            pass

    html += "<tr style='border-bottom:1px solid #21262d;'>"
    html += f"<td style='padding:12px 8px; color:#c9d1d9; font-weight:600;'>{name}</td>"
    html += f"<td style='padding:12px 8px; color:#8b949e; font-size:.85rem;'>{date}</td>"
    html += f"<td style='padding:12px 8px; color:#8b949e; font-size:.85rem;'>{day_name}</td>"
    html += f"<td style='padding:12px 8px; color:#3fb950; font-size:.85rem;'>{time_in or '—'}</td>"
    html += f"<td style='padding:12px 8px; color:#f85149; font-size:.85rem;'>{time_out or '—'}</td>"
    html += f"<td style='padding:12px 8px; color:#d29922; font-size:.85rem;'>{dur_text}</td>"
    html += f"<td style='padding:12px 8px;'>{badge(status, color)}</td>"
    html += f"<td style='padding:12px 8px; color:#8b949e; font-size:.85rem;'>{leave_reason or '—'}</td>"
    html += "</tr>"

html += "</tbody></table></div>"
st.markdown(html, unsafe_allow_html=True)

# ── Excel Export ──
st.markdown("<br>", unsafe_allow_html=True)
section_header("Export")

df = pd.DataFrame(records, columns=["User","Date","In Time","Out Time","Leave Reason"])
df["Day"] = df["Date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%A"))

def get_status_label(row):
    _, s, _ = resolve_status(row["Date"], row["In Time"], row["Out Time"], row["Leave Reason"])
    return s

df["Status"]       = df.apply(get_status_label, axis=1)
df["In Time"]      = df["In Time"].fillna("—")
df["Out Time"]     = df["Out Time"].fillna("—")
df["Leave Reason"] = df["Leave Reason"].fillna("None")
df = df[["User","Date","Day","In Time","Out Time","Status","Leave Reason"]]

output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Attendance")
excel_data = output.getvalue()

st.download_button(
    label="📥 Download Excel Report",
    data=excel_data,
    file_name=f"attendance_{selected_user}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)