import streamlit as st

def require_login():
    user = st.session_state.get("user")
    if not user:
        st.switch_page("Dashboard.py")
    else:
        with st.sidebar:
            st.markdown("<br><br><hr>", unsafe_allow_html=True)
            if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
                st.session_state["user"] = None
                st.rerun()

def get_user():
    return st.session_state.get("user")