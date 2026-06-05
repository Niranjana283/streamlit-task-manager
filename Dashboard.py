import streamlit as st
from auth import login, register, set_session
from database import cursor
from theme import inject_theme, section_header, badge

st.set_page_config(page_title="TaskFlow Pro", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
inject_theme()

# ── Session bootstrap ──
if "user" not in st.session_state:
    st.session_state["user"] = None

user = st.session_state["user"]

# =========================================================
# NOT LOGGED IN — Premium Login Page
# =========================================================
if user is None:
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none; }
        [data-testid="stSidebar"] { display: none; }
    </style>
    <div style="text-align:center;margin-top:60px;margin-bottom:32px;">
        <span style="font-size:3rem;">⚡</span>
        <h1 style="color:#e6edf3;font-size:2rem;font-weight:800;margin:10px 0 4px;">TaskFlow Pro</h1>
        <p style="color:#8b949e;font-size:.95rem;margin:0;">Team productivity, simplified.</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        menu = st.selectbox("", ["🔑 Login", "📝 Register"], label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        if menu == "🔑 Login":
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", placeholder="••••••••", type="password")
                submitted = st.form_submit_button("Sign In →", use_container_width=True)
            if submitted:
                result = login(username, password)
                if result:
                    set_session(result)
                    st.success("Welcome back! 🎉")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        else:
            with st.form("register_form"):
                username = st.text_input("Username", placeholder="Choose a username")
                password = st.text_input("Password", placeholder="••••••••", type="password")
                role     = st.selectbox("Role", ["user", "admin"])
                submitted = st.form_submit_button("Create Account →", use_container_width=True)
            if submitted:
                if register(username, password, role):
                    st.success("✅ Account created! Please login.")
                else:
                    st.error("❌ Username already taken.")

    st.stop()

# =========================================================
# LOGGED IN — Dashboard
# =========================================================
is_admin = user["role"] == "admin"
role_color = "#f78166" if is_admin else "#3fb950"
role_label = "Admin" if is_admin else user["role"].capitalize()

# Live stats
total_users     = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
total_tasks     = cursor.execute("SELECT COUNT(*) FROM tasks WHERE sub_task IS NOT NULL").fetchone()[0]
completed_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed=1").fetchone()[0]
pending_tasks   = total_tasks - completed_tasks

# Hero banner
st.markdown(f"""
<div style="
    background:linear-gradient(135deg,#161b22 0%,#0d1117 100%);
    border:1px solid #30363d; border-radius:16px;
    padding:30px 36px; margin-bottom:28px;
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;
">
    <div>
        <p style="color:#8b949e;font-size:.75rem;text-transform:uppercase;letter-spacing:1.5px;margin:0 0 6px;">
            Welcome back
        </p>
        <h1 style="color:#e6edf3;font-size:1.9rem;font-weight:800;margin:0 0 12px;">
            👋 {user['username']}
        </h1>
        <span style="background:{role_color}22;color:{role_color};border:1px solid {role_color}44;
              border-radius:20px;padding:4px 14px;font-size:.78rem;font-weight:600;">
            ⬡ {role_label}
        </span>
    </div>
    <div style="text-align:right;">
        <p style="color:#8b949e;font-size:.75rem;margin:0 0 4px;">Platform</p>
        <p style="color:#58a6ff;font-size:1.6rem;font-weight:800;margin:0;">⚡ TaskFlow Pro</p>
    </div>
</div>
""", unsafe_allow_html=True)

# KPI cards
section_header("Overview")

def kpi(icon, label, value, color):
    return f"""
    <div style="background:#161b22;border:1px solid #30363d;border-left:4px solid {color};
                border-radius:12px;padding:20px 22px;">
        <p style="color:#8b949e;font-size:.75rem;text-transform:uppercase;
                  letter-spacing:1px;margin:0 0 10px;">{icon} {label}</p>
        <p style="color:#e6edf3;font-size:2.1rem;font-weight:800;margin:0;line-height:1;">{value}</p>
    </div>"""

c1, c2, c3, c4 = st.columns(4)
c1.markdown(kpi("👥", "Total Users",  total_users,     "#58a6ff"), unsafe_allow_html=True)
c2.markdown(kpi("📋", "Total Tasks",  total_tasks,     "#bc8cff"), unsafe_allow_html=True)
c3.markdown(kpi("✅", "Completed",    completed_tasks, "#3fb950"), unsafe_allow_html=True)
c4.markdown(kpi("⏳", "Pending",      pending_tasks,   "#d29922"), unsafe_allow_html=True)

# Nav cards
st.markdown("<br>", unsafe_allow_html=True)
section_header("Quick Navigation")

def nav_card(icon, title, desc, color):
    return f"""
    <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;
                padding:22px 20px;transition:border-color .2s;cursor:pointer;">
        <div style="font-size:1.8rem;margin-bottom:10px;">{icon}</div>
        <p style="color:{color};font-size:.95rem;font-weight:700;margin:0 0 6px;">{title}</p>
        <p style="color:#8b949e;font-size:.8rem;margin:0;line-height:1.5;">{desc}</p>
    </div>"""

n1,n2,n3,n4,n5 = st.columns(5)

with n1:
    st.markdown(nav_card("👥","User Management","Manage users & roles","#58a6ff"), unsafe_allow_html=True)
    if st.button("Go →", key="nav_users", use_container_width=True):
        st.switch_page("pages/1_User_Management.py")

with n2:
    st.markdown(nav_card("📋","Task Management","Create & track weekly tasks","#bc8cff"), unsafe_allow_html=True)
    if st.button("Go →", key="nav_tasks", use_container_width=True):
        st.switch_page("pages/2_Task_Management.py")

with n3:
    st.markdown(nav_card("📂","All Tasks","View all tasks at a glance","#3fb950"), unsafe_allow_html=True)
    if st.button("Go →", key="nav_alltasks", use_container_width=True):
        st.switch_page("pages/3_All_Tasks.py")

with n4:
    st.markdown(nav_card("📊","Reports","Export PDF task reports","#f78166"), unsafe_allow_html=True)
    if st.button("Go →", key="nav_reports", use_container_width=True):
        st.switch_page("pages/4_Report.py")

with n5:
    st.markdown(nav_card("🗓️","Attendance","Track daily attendance","#d29922"), unsafe_allow_html=True)
    if st.button("Go →", key="nav_attendance", use_container_width=True):
        st.switch_page("pages/5_Attendance.py")

with st.sidebar:
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    if st.button("🚪 Logout", key="dash_logout", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()
