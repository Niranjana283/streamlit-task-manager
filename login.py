import streamlit as st
from auth import login, register, set_session

st.title("🔐 Login System")

menu = st.selectbox("Choose", ["Login", "Register"])

# ---------------- LOGIN ----------------
if menu == "Login":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(username, password)

        if user:
            set_session(user)
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

# ---------------- REGISTER ----------------
elif menu == "Register":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Select Role", ["admin", "intern"])

    if st.button("Register"):
        if register(username, password, role):
            st.success("Account created successfully ✅")
        else:
            st.error("User already exists ❌")