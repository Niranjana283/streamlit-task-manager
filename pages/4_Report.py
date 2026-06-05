import streamlit as st
from database import cursor
import pandas as pd
from io import BytesIO
from auth_guard import require_login, get_user
from theme import inject_theme, page_header, section_header, badge, PRIORITY_COLOR

st.set_page_config(page_title="Reports · TaskFlow", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
inject_theme()
require_login()
user = get_user()

# PDF imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

page_header("📊", "Task Report", "Generate and export filtered task reports")

# ── Load data ──
data = cursor.execute("""
SELECT users.name, tasks.main_task, tasks.sub_task,
       tasks.priority, tasks.due_date, tasks.end_date, tasks.completed
FROM tasks
JOIN users ON tasks.user_id = users.id
WHERE tasks.sub_task IS NOT NULL
""").fetchall()

if not data:
    st.info("No task data available yet.")
    st.stop()

df = pd.DataFrame(data, columns=["User","Main Task","Sub Task","Priority","Start Date","End Date","Completed"])
df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
df["End Date"]   = pd.to_datetime(df["End Date"],   errors="coerce")
df = df.dropna(subset=["Start Date"])
df["End Date"] = df["End Date"].fillna(df["Start Date"])

# ── Sidebar filters ──
st.sidebar.markdown("### 🔍 Filters")
users_list    = df["User"].unique().tolist()
selected_user = st.sidebar.selectbox("👤 User", users_list)
filtered_df   = df[df["User"] == selected_user]

min_date = filtered_df["Start Date"].min().date()
max_date = filtered_df["End Date"].max().date()

st.sidebar.markdown("---")
st.sidebar.markdown("**📅 Date Range**")
from_date = st.sidebar.date_input("From", min_date)
to_date   = st.sidebar.date_input("To",   max_date)

from_dt = pd.to_datetime(from_date)
to_dt   = pd.to_datetime(to_date)

filtered_df = filtered_df[
    (filtered_df["Start Date"] <= to_dt) &
    (filtered_df["End Date"]   >= from_dt)
]

# ── KPIs ──
section_header("Summary")
total_f   = len(filtered_df)
done_f    = filtered_df["Completed"].sum()
pending_f = total_f - done_f

k1, k2, k3 = st.columns(3)
def kpi(icon, label, value, color):
    return (f"<div style='background:#161b22;border:1px solid #30363d;"
            f"border-left:4px solid {color};border-radius:12px;padding:18px 22px;'>"
            f"<p style='color:#8b949e;font-size:.75rem;text-transform:uppercase;"
            f"letter-spacing:1px;margin:0 0 8px;'>{icon} {label}</p>"
            f"<p style='color:#e6edf3;font-size:1.9rem;font-weight:800;margin:0;'>{value}</p></div>")

k1.markdown(kpi("📋","Total Tasks",total_f,"#58a6ff"),   unsafe_allow_html=True)
k2.markdown(kpi("✅","Completed",  int(done_f),"#3fb950"),unsafe_allow_html=True)
k3.markdown(kpi("⏳","Pending",    int(pending_f),"#d29922"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Task cards ──
section_header(f"Tasks · {selected_user} · {from_date} → {to_date}")

if filtered_df.empty:
    st.info("No tasks found for the selected date range.")
else:
    for main_task in filtered_df["Main Task"].unique():
        subset = filtered_df[filtered_df["Main Task"] == main_task]

        st.markdown(f"""
        <div style='background:#161b22;border:1px solid #30363d;border-radius:12px;
                    padding:18px 22px;margin-bottom:14px;'>
            <p style='color:#58a6ff;font-size:1rem;font-weight:700;margin:0 0 12px;'>
                📌 {main_task}
            </p>
        """, unsafe_allow_html=True)

        for _, row in subset.iterrows():
            pcolor = PRIORITY_COLOR.get(row["Priority"], "#8b949e")
            scolor = "#3fb950" if row["Completed"] == 1 else "#d29922"
            status = "Done" if row["Completed"] == 1 else "Pending"
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;
                        padding:8px 0;border-bottom:1px solid #21262d;'>
                <span style='color:#8b949e;font-size:.8rem;min-width:90px;'>
                    {row['Start Date'].date()} →
                </span>
                <span style='color:#c9d1d9;flex:1;'>{row['Sub Task']}</span>
                {badge(row['Priority'], pcolor)}
                {badge(status, scolor)}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── PDF Export ──
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Export Report")

    def generate_pdf(data_df):
        buffer  = BytesIO()
        doc     = SimpleDocTemplate(buffer, leftMargin=.6*inch, rightMargin=.6*inch,
                                    topMargin=.7*inch, bottomMargin=.6*inch)
        styles  = getSampleStyleSheet()
        content = []

        title_style = ParagraphStyle("TF", parent=styles["Title"],
                                     textColor=colors.HexColor("#1f6feb"), fontSize=18)
        h2_style    = ParagraphStyle("H2", parent=styles["Heading2"],
                                     textColor=colors.HexColor("#388bfd"), fontSize=12)
        body_style  = styles["Normal"]

        content.append(Paragraph("⚡ TaskFlow Pro — Task Report", title_style))
        content.append(Spacer(1, 8))
        content.append(Paragraph(
            f"User: <b>{selected_user}</b> &nbsp;|&nbsp; Period: <b>{from_date} – {to_date}</b>",
            body_style
        ))
        content.append(Spacer(1, 16))

        for main_task in data_df["Main Task"].unique():
            subset = data_df[data_df["Main Task"] == main_task]
            content.append(Paragraph(f"📌 {main_task}", h2_style))
            content.append(Spacer(1, 6))

            tbl_data = [["Sub Task", "Priority", "Start Date", "End Date", "Status"]]
            for _, row in subset.iterrows():
                tbl_data.append([
                    row["Sub Task"],
                    row["Priority"],
                    str(row["Start Date"].date()),
                    str(row["End Date"].date()),
                    "Done" if row["Completed"] == 1 else "Pending",
                ])

            tbl = Table(tbl_data, colWidths=[2.5*inch, 1*inch, 1.1*inch, 1.1*inch, .9*inch])
            tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,0),  colors.HexColor("#1f6feb")),
                ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
                ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
                ("FONTSIZE",    (0,0), (-1,-1), 8),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f4ff"), colors.white]),
                ("GRID",        (0,0), (-1,-1), .4, colors.HexColor("#d0d7de")),
                ("ROUNDEDCORNERS", [4]),
                ("TOPPADDING",  (0,0), (-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ]))
            content.append(tbl)
            content.append(Spacer(1, 14))

        doc.build(content)
        buffer.seek(0)
        return buffer

    pdf = generate_pdf(filtered_df)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf,
        file_name=f"taskreport_{selected_user}_{from_date}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )