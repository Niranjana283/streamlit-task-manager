import streamlit as st
from database import cursor, conn

st.title("👤 User Management")

# Add User
with st.form("add_user"):
    name = st.text_input("Enter User Name")
    submit = st.form_submit_button("Add User")

    if submit:
        try:
            cursor.execute(
                "INSERT INTO users (name) VALUES (?)",
                (name,)
            )
            conn.commit()
            st.success("User Added")
        except:
            st.error("User already exists")

users = cursor.execute("SELECT * FROM users").fetchall()

st.subheader("Existing Users")

for user in users:
    col1, col2 = st.columns([4,1])

    col1.write(user[1])

    if col2.button("Delete", key=user[0]):
        cursor.execute(
            "DELETE FROM users WHERE id=?",
            (user[0],)
        )
        conn.commit()
        st.rerun()