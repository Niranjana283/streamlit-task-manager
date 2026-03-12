import streamlit as st
from database import cursor
import pandas as pd

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="Task Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Task Manager Dashboard")
st.caption("Quick overview of task progress")

# -------- FETCH DATA --------
total_tasks = cursor.execute(
    "SELECT COUNT(*) FROM tasks"
).fetchone()[0]

completed_tasks = cursor.execute(
    "SELECT COUNT(*) FROM tasks WHERE completed = 1"
).fetchone()[0]

pending_tasks = cursor.execute(
    "SELECT COUNT(*) FROM tasks WHERE completed = 0"
).fetchone()[0]

# -------- METRICS --------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📋 Total Tasks", total_tasks)

with col2:
    st.metric("✅ Completed Tasks", completed_tasks)

with col3:
    st.metric("⏳ Pending Tasks", pending_tasks)

st.divider()

# -------- PROGRESS BAR --------
st.subheader("📈 Overall Progress")

if total_tasks > 0:
    progress = completed_tasks / total_tasks
else:
    progress = 0

st.progress(progress)
st.write(f"**{int(progress*100)}% of tasks completed**")

st.divider()



# -------- USERS OVERVIEW --------
st.subheader("👥 Users Overview")

users = cursor.execute("""
SELECT id, name
FROM users
ORDER BY name
""").fetchall()

if users:

    df_users = pd.DataFrame(users, columns=[
        "User ID",
        "Name"
    ])

    st.dataframe(df_users, use_container_width=True)

else:
    st.info("No users available.")