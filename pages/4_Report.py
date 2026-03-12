import streamlit as st
from database import cursor
import pandas as pd

st.title("📊 Task Report")

# ---------------- LOAD DATA ----------------
data = cursor.execute("""
SELECT users.name,
       tasks.main_task,
       tasks.sub_task,
       tasks.priority,
       tasks.due_date,
       tasks.end_date
FROM tasks
JOIN users ON tasks.user_id = users.id
""").fetchall()

if not data:
    st.info("No tasks available.")
    st.stop()

# ---------------- CREATE DATAFRAME ----------------
df = pd.DataFrame(data, columns=[
    "User","Main Task","Sub Task","Priority","Start Date","End Date"
])

# ---------------- DATE FORMAT ----------------
df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
df["End Date"] = pd.to_datetime(df["End Date"], errors="coerce")

df = df.dropna(subset=["Start Date"])
df["End Date"] = df["End Date"].fillna(df["Start Date"])

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Filters")

# User Filter
users = df["User"].unique()

selected_user = st.sidebar.selectbox(
    "👤 Select User",
    users
)

df = df[df["User"] == selected_user]

# ---------------- DATE RANGE FILTER ----------------
st.sidebar.subheader("📅 Select Date Range")

min_date = df["Start Date"].min().date()
max_date = df["End Date"].max().date()

from_date = st.sidebar.date_input("From Date", min_date)
to_date = st.sidebar.date_input("To Date", max_date)

from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)

# Filter tasks in selected range
filtered_df = df[
    (df["Start Date"] <= to_date) &
    (df["End Date"] >= from_date)
]

# ---------------- SHOW REPORT ----------------
st.subheader(f"📋 Tasks from {from_date.date()} to {to_date.date()}")

if filtered_df.empty:
    st.info("No tasks found for selected dates.")

else:
    
    for main_task in filtered_df["Main Task"].unique():

        st.markdown(f"### 📌 {main_task}")

        sub_tasks = filtered_df[
            filtered_df["Main Task"] == main_task
        ]

        for _, row in sub_tasks.iterrows():

            st.success(
                f"✔ {row['Sub Task']} | Priority: {row['Priority']} | "
                f"{row['Start Date'].date()} → {row['End Date'].date()}"
            )