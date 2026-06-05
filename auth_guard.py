import streamlit as st

def require_login():
    user = st.session_state.get("user")
    if not user:
        st.switch_page("Dashboard.py")

def get_user():
    return st.session_state.get("user")