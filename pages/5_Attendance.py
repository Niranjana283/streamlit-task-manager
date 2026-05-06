import streamlit as st
from database import cursor
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Attendance", layout="wide")

st.title("📊 Attendance Dashboard (From Tasks)")

# ---------------- MOBILE TOGGLE ----------------
is_mobile = st.sidebar.checkbox("📱 Mobile View", value=False)

# ---------------- HOLIDAYS ----------------
HOLIDAYS = [
    "2026-01-26",
    "2026-08-15",
    "2026-10-02",
]

# ---------------- FETCH USERS ----------------
users = cursor.execute("SELECT id, name FROM users").fetchall()

user_dict = {u[1]: u[0] for u in users}
user_names = ["All"] + list(user_dict.keys())

selected_user = st.selectbox("👤 Filter by User", user_names)

# ---------------- FETCH DATA ----------------
if selected_user == "All":
    records = cursor.execute(
        """
        SELECT u.name, t.due_date, t.time_in, t.time_out, t.leave_reason
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
        SELECT u.name, t.due_date, t.time_in, t.time_out, t.leave_reason
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

    # ================= MOBILE VIEW =================
    if is_mobile:

        for r in records:
            name, date, time_in, time_out, leave_reason = r

            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")

            is_weekend = date_obj.weekday() >= 5
            is_holiday = date in HOLIDAYS

            # Status logic
            if is_weekend or is_holiday:
                status = "🟡 Not Working Day"
                reason = "Weekend/Holiday"
            elif leave_reason:
                status = "❌ Leave"
                reason = leave_reason
            elif time_in and time_out:
                status = "✅ Present"
                reason = "None"
            else:
                status = "⚠️ Partial"
                reason = "Not specified"

            # Card UI
            with st.container():
                st.markdown(f"""
### 👤 {name}
📅 {date} ({day_name})  
🟢 In: {time_in if time_in else "-"}  
🔴 Out: {time_out if time_out else "-"}  
📌 Status: {status}  
🏖️ Reason: {reason}
""")
                st.divider()

    # ================= DESKTOP VIEW =================
    else:

        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

        col1.markdown("**👤 User**")
        col2.markdown("**📅 Date**")
        col3.markdown("**📆 Day**")
        col4.markdown("**🟢 In Time**")
        col5.markdown("**🔴 Out Time**")
        col6.markdown("**📌 Status**")
        col7.markdown("**🏖️ Reason**")

        st.markdown("---")

        for r in records:
            name, date, time_in, time_out, leave_reason = r

            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")

            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

            col1.write(name)
            col2.write(date)
            col3.write(day_name)
            col4.write(time_in if time_in else "-")
            col5.write(time_out if time_out else "-")

            is_weekend = date_obj.weekday() >= 5
            is_holiday = date in HOLIDAYS

            if is_weekend or is_holiday:
                col6.info("Not Working Day 🟡")
                col7.write("Weekend/Holiday")

            elif leave_reason:
                col6.error("Leave ❌")
                col7.write(leave_reason)

            elif time_in and time_out:
                col6.success("Present ✅")
                col7.write("None")

            else:
                col6.warning("Partial ⚠️")
                col7.write("Not specified")

    # ======================================================
    # 📥 EXPORT TO EXCEL
    # ======================================================

    st.markdown("### 📥 Export Data")

    df = pd.DataFrame(records, columns=[
        "User", "Date", "In Time", "Out Time", "Leave Reason"
    ])

    df["Day"] = df["Date"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%A")
    )

    def get_status(row):
        date_obj = datetime.strptime(row["Date"], "%Y-%m-%d")

        is_weekend = date_obj.weekday() >= 5
        is_holiday = row["Date"] in HOLIDAYS

        if is_weekend or is_holiday:
            return "Not Working Day"
        elif row["Leave Reason"]:
            return "Leave"
        elif row["In Time"] and row["Out Time"]:
            return "Present"
        else:
            return "Partial"

    df["Status"] = df.apply(get_status, axis=1)

    df["In Time"] = df["In Time"].fillna("-")
    df["Out Time"] = df["Out Time"].fillna("-")
    df["Leave Reason"] = df["Leave Reason"].fillna("None")

    df = df[["User", "Date", "Day", "In Time", "Out Time", "Status", "Leave Reason"]]

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")

    excel_data = output.getvalue()

    st.download_button(
        label="📥 Export to Excel",
        data=excel_data,
        file_name=f"attendance_{selected_user}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )