import streamlit as st
from database import cursor

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Task Dashboard",
    page_icon="📊",
    layout="wide"
)

# ======================================================
# 📊 MAIN DASHBOARD
# ======================================================

st.title("📊 Task Manager Dashboard")
st.caption("Quick overview of task progress")

# -------- FETCH DATA --------
total_tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
completed_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1").fetchone()[0]
pending_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 0").fetchone()[0]

# -------- METRICS --------
col1, col2, col3 = st.columns(3)

col1.metric("📋 Total Tasks", total_tasks)
col2.metric("✅ Completed Tasks", completed_tasks)
col3.metric("⏳ Pending Tasks", pending_tasks)

st.divider()

# -------- PROGRESS BAR --------
st.subheader("📈 Overall Progress")

progress = completed_tasks / total_tasks if total_tasks > 0 else 0
st.progress(progress)
st.write(f"**{int(progress*100)}% of tasks completed**")

st.divider()

# ======================================================
# 👥 USER-WISE DASHBOARD
# ======================================================

st.subheader("👥 User Task Overview")

user_stats = cursor.execute("""
SELECT 
    u.name,
    COUNT(t.id) as total,
    SUM(CASE WHEN t.completed = 1 THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN t.completed = 0 THEN 1 ELSE 0 END) as pending
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id
ORDER BY u.name
""").fetchall()

if user_stats:

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown("**👤 User**")
    col2.markdown("**📋 Total**")
    col3.markdown("**✅ Completed**")
    col4.markdown("**⏳ Pending**")
    col5.markdown("**📈 Progress**")

    st.markdown("---")

    for u in user_stats:
        name, total, completed, pending = u

        total = total or 0
        completed = completed or 0
        pending = pending or 0

        progress = (completed / total) if total > 0 else 0

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.write(name)
        c2.write(total)
        c3.success(completed)
        c4.warning(pending)

        c5.progress(progress)
        c5.write(f"{int(progress*100)}%")

else:
    st.info("No user data available")