
import streamlit as st
from database import cursor, conn
from datetime import date

st.title("📋 Weekly Task Management")

# ---------------- GET USERS ----------------
users = cursor.execute("SELECT * FROM users").fetchall()

if not users:
    st.warning("Add a user first")
    st.stop()

user_dict = {u[1]: u[0] for u in users}

selected_user = st.selectbox(
    "👤 Select User",
    list(user_dict.keys())
)

user_id = user_dict[selected_user]


# ======================================================
# 1️⃣ CREATE MAIN TASK (WEEK TASK)
# ======================================================

st.subheader("📌 Create Weekly Main Task")

with st.form("main_task_form"):

    main_task = st.text_input("Main Task")

    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High"]
    )

    start_date = st.date_input("Start Date")

    end_date = st.date_input("End Date")

    submit_main = st.form_submit_button("Create Main Task")

    if submit_main:

        cursor.execute(
            """
            INSERT INTO tasks (
                user_id,
                main_task,
                priority,
                due_date,
                completed_at,
                completed
            )
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                main_task,
                priority,
                str(start_date),
                str(end_date)
            )
        )

        conn.commit()

        st.success("Main Task Created ✅")
        st.rerun()


# ======================================================
# 2️⃣ SELECT MAIN TASK
# ======================================================

main_tasks = cursor.execute(
    """
    SELECT DISTINCT main_task
    FROM tasks
    WHERE user_id=? AND main_task IS NOT NULL
    """,
    (user_id,)
).fetchall()

if not main_tasks:
    st.info("Create a main task first")
    st.stop()

main_task_list = [m[0] for m in main_tasks]

selected_main_task = st.selectbox(
    "📌 Select Main Task",
    main_task_list
)


# ======================================================
# 3️⃣ ADD DAILY SUB TASK
# ======================================================

st.subheader("📝 Add Daily Activity")

with st.form("sub_task_form"):

    activity_date = st.date_input("Activity Date")

    sub_task = st.text_input("Daily Activity")

    submit_sub = st.form_submit_button("Add Activity")

    if submit_sub:

        cursor.execute(
            """
            INSERT INTO tasks (
                user_id,
                main_task,
                sub_task,
                due_date,
                completed
            )
            VALUES (?, ?, ?, ?, 0)
            """,
            (
                user_id,
                selected_main_task,
                sub_task,
                str(activity_date)
            )
        )

        conn.commit()

        st.success("Daily Activity Added ✅")
        st.rerun()


# ======================================================
# 4️⃣ SHOW ACTIVITIES
# ======================================================

st.subheader("📅 Weekly Activities")

activities = cursor.execute(
    """
    SELECT id, sub_task, due_date, completed
    FROM tasks
    WHERE user_id=? AND main_task=? AND sub_task IS NOT NULL
    ORDER BY due_date
    """,
    (user_id, selected_main_task)
).fetchall()

if not activities:
    st.info("No activities yet")

else:

    for act in activities:

        col1, col2, col3, col4 = st.columns([6,1,1,1])

        task_text = f"📅 {act[2]} → {act[1]}"

        # Completed style
        if act[3] == 1:
            col1.markdown(f"~~{task_text}~~")
        else:
            col1.write(task_text)

        # ---------------- COMPLETE ----------------
        if col2.button("✅", key=f"complete{act[0]}"):

            cursor.execute(
                "UPDATE tasks SET completed=1 WHERE id=?",
                (act[0],)
            )

            conn.commit()
            st.rerun()

        # ---------------- EDIT ----------------
        if col3.button("✏️", key=f"edit{act[0]}"):

            new_text = st.text_input(
                "Edit Activity",
                value=act[1],
                key=f"edit_text{act[0]}"
            )

            if st.button("Save", key=f"save{act[0]}"):

                cursor.execute(
                    "UPDATE tasks SET sub_task=? WHERE id=?",
                    (new_text, act[0])
                )

                conn.commit()
                st.rerun()

        # ---------------- DELETE ----------------
        if col4.button("❌", key=f"delete{act[0]}"):

            cursor.execute(
                "DELETE FROM tasks WHERE id=?",
                (act[0],)
            )

            conn.commit()
            st.rerun()

