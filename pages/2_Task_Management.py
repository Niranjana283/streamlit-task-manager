import streamlit as st
from database import cursor, conn
from datetime import datetime, timedelta

# ---------------- VALIDATE TIME ----------------
def validate_time(t):
    try:
        datetime.strptime(t, "%H:%M")
        return True
    except:
        return False

st.title("📋 Weekly Task Management")

# ---------------- GET USERS ----------------
users = cursor.execute("SELECT * FROM users").fetchall()

if not users:
    st.warning("Add a user first")
    st.stop()

user_dict = {u[1]: u[0] for u in users}

selected_user = st.selectbox("👤 Select User", list(user_dict.keys()))
user_id = user_dict[selected_user]

# ======================================================
# 1️⃣ CREATE MAIN TASK
# ======================================================

st.subheader("📌 Create Weekly Main Task")

with st.form("main_task_form"):

    main_task = st.text_input("Main Task")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    submit_main = st.form_submit_button("Create Main Task")

    if submit_main:
        if not main_task.strip():
            st.error("Main task cannot be empty")
            st.stop()

        if start_date > end_date:
            st.error("Start date cannot be after end date")
            st.stop()

        cursor.execute(
            """
            INSERT INTO tasks (
                user_id,
                main_task,
                priority,
                start_date,
                end_date,
                completed
            )
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (user_id, main_task, priority, str(start_date), str(end_date))
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
selected_main_task = st.selectbox("📌 Select Main Task", main_task_list)

# ======================================================
# 3️⃣ ADD DAILY SUB TASK WITH LEAVE REASON
# ======================================================

st.subheader("📝 Add Daily Activity")

with st.form("sub_task_form"):

    activity_date = st.date_input("Activity Date")
    sub_task = st.text_input("Daily Activity")

    st.markdown("⏰ **Work Time**")

    col1, col2 = st.columns(2)

    with col1:
        time_in = st.text_input("In (HH:MM)", placeholder="09:00")

    with col2:
        time_out = st.text_input("Out (HH:MM)", placeholder="18:00")

    # ✅ NEW FIELD
    leave_reason = st.text_input("🏖️ Leave Reason (optional)")

    submit_sub = st.form_submit_button("Add Activity")

    if submit_sub:

        if not sub_task.strip() and not leave_reason.strip():
            st.error("Enter activity or leave reason")
            st.stop()

        if time_in and time_out:
            if not validate_time(time_in) or not validate_time(time_out):
                st.error("❌ Enter time in HH:MM format")
                st.stop()

        # If leave entered → auto mark task
        if leave_reason.strip():
            sub_task = "Leave"

        cursor.execute(
            """
            INSERT INTO tasks (
                user_id,
                main_task,
                sub_task,
                due_date,
                time_in,
                time_out,
                leave_reason,
                completed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                selected_main_task,
                sub_task,
                str(activity_date),
                time_in,
                time_out,
                leave_reason
            )
        )
        conn.commit()
        st.success("Activity Added ✅")
        st.rerun()

# ======================================================
# 4️⃣ SHOW ACTIVITIES
# ======================================================

st.subheader("📅 Weekly Activities")

activities = cursor.execute(
    """
    SELECT id, sub_task, due_date, completed, time_in, time_out, leave_reason
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

        # Duration
        duration_text = ""
        if act[4] and act[5]:
            try:
                t1 = datetime.strptime(act[4], "%H:%M")
                t2 = datetime.strptime(act[5], "%H:%M")

                if t2 < t1:
                    duration = (t2 + timedelta(days=1)) - t1
                else:
                    duration = t2 - t1

                duration_text = f" | ⏱️ {duration}"
            except:
                pass

        # Leave text
        leave_text = f" | 🏖️ {act[6]}" if act[6] else ""

        task_text = f"📅 {act[2]} → {act[1]} ⏰ {act[4]} - {act[5]}{duration_text}{leave_text}"

        if act[3] == 1:
            col1.markdown(f"~~{task_text}~~")
        else:
            col1.write(task_text)

        # ✅ COMPLETE
        if col2.button("✅", key=f"complete{act[0]}"):
            cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (act[0],))
            conn.commit()
            st.rerun()

        # ✏️ EDIT
        if col3.button("✏️", key=f"edit{act[0]}"):

            new_text = st.text_input("Edit Activity", value=act[1], key=f"text{act[0]}")

            col_e1, col_e2 = st.columns(2)

            with col_e1:
                new_time_in = st.text_input("In", value=act[4] or "", key=f"timein{act[0]}")

            with col_e2:
                new_time_out = st.text_input("Out", value=act[5] or "", key=f"timeout{act[0]}")

            # ✅ Edit Leave
            new_leave = st.text_input(
                "Leave Reason",
                value=act[6] or "",
                key=f"leave{act[0]}"
            )

            if st.button("Save", key=f"save{act[0]}"):

                if new_time_in and new_time_out:
                    if not validate_time(new_time_in) or not validate_time(new_time_out):
                        st.error("Invalid time format")
                        st.stop()

                cursor.execute(
                    """
                    UPDATE tasks 
                    SET sub_task=?, time_in=?, time_out=?, leave_reason=? 
                    WHERE id=?
                    """,
                    (new_text, new_time_in, new_time_out, new_leave, act[0])
                )
                conn.commit()
                st.rerun()

        # ❌ DELETE
        if col4.button("❌", key=f"delete{act[0]}"):
            cursor.execute("DELETE FROM tasks WHERE id=?", (act[0],))
            conn.commit()
            st.rerun()