from database import cursor, conn
import streamlit as st

users_db = {}

# ---------------- REGISTER ----------------
def register(username, password, role="user"):
    try:
        cursor.execute(
            "INSERT INTO users (name, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        return True
    except:
        return False


# ---------------- LOGIN ----------------
def login(username, password):
    cursor.execute(
        "SELECT id, name, role FROM users WHERE name=? AND password=?",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        return {
            "id": user[0],
            "username": user[1],
            "role": user[2]
        }

    return None

# ---------------- SESSION ----------------
def set_session(user):
    import streamlit as st
    st.session_state["user"] = user