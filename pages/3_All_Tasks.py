import streamlit as st
from database import cursor

st.title("📋 All Users Tasks")

# ---------------- GET USERS ----------------
users = cursor.execute("SELECT name FROM users").fetchall()
user_list = [user[0] for user in users]

# ---------------- FILTERS ----------------
col1, col2 = st.columns(2)

with col1:
    user_filter = st.selectbox(
        "👤 Filter by User",
        ["All Users"] + user_list
    )

with col2:
    status_filter = st.selectbox(
        "📌 Status",
        ["All", "Completed", "Pending"]
    )

# ---------------- QUERY TASKS ----------------
query = """
SELECT users.name,
       tasks.main_task,
       tasks.sub_task,
       tasks.priority,
       tasks.due_date,
       tasks.end_date,
       tasks.completed
FROM tasks
JOIN users ON tasks.user_id = users.id
"""

params = []

# User filter
if user_filter != "All Users":
    query += " WHERE users.name=?"
    params.append(user_filter)

query += " ORDER BY tasks.due_date"

all_tasks = cursor.execute(query, params).fetchall()

# ---------------- DISPLAY TABLE ----------------
if not all_tasks:
    st.info("No tasks available.")

else:

    table_data = []

    for row in all_tasks:

        status = "Completed" if row[6] == 1 else "Pending"

        # Status filter
        if status_filter != "All" and status_filter != status:
            continue

        table_data.append({
            "User Name": row[0],
            "Main Task": row[1],
            "Sub Task": row[2],
            "Priority": row[3],
            "Start Date": row[4],
            "End Date": row[5],
            "Status": "✅ Completed" if row[6] == 1 else "⏳ Pending"
        })

    st.dataframe(table_data, use_container_width=True)