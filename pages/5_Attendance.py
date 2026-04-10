import streamlit as st
from database import cursor

st.title("📊 Attendance Dashboard (From Tasks)")

# ---------------- FETCH USERS ----------------
users = cursor.execute("SELECT id, name FROM users").fetchall()

user_dict = {u[1]: u[0] for u in users}  # name -> id
user_names = ["All"] + list(user_dict.keys())

# ---------------- DROPDOWN ----------------
selected_user = st.selectbox("👤 Filter by User", user_names)

# ---------------- FETCH DATA BASED ON FILTER ----------------
if selected_user == "All":
    records = cursor.execute(
        """
        SELECT u.name, t.due_date, t.time_in, t.time_out
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        WHERE t.sub_task IS NOT NULL
        ORDER BY t.due_date DESC
        """
    ).fetchall()
else:
    user_id = user_dict[selected_user]

    records = cursor.execute(
        """
        SELECT u.name, t.due_date, t.time_in, t.time_out
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        WHERE t.user_id = ? AND t.sub_task IS NOT NULL
        ORDER BY t.due_date DESC
        """,
        (user_id,)
    ).fetchall()

# ---------------- DISPLAY ----------------
st.subheader("📋 Attendance Table")

if not records:
    st.info("No data available")

else:
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown("**👤 User**")
    col2.markdown("**📅 Date**")
    col3.markdown("**🟢 In Time**")
    col4.markdown("**🔴 Out Time**")
    col5.markdown("**📌 Status**")

    st.markdown("---")

    for r in records:
        name, date, time_in, time_out = r

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.write(name)
        col2.write(date)
        col3.write(time_in if time_in else "-")
        col4.write(time_out if time_out else "-")

        if time_in and time_out:
            col5.success("Present ✅")
        else:
            col5.error("Leave ❌")