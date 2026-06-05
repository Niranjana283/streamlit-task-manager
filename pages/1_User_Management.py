import streamlit as st
from database import cursor, conn
from auth_guard import require_login, get_user
from theme import inject_theme, page_header, section_header, badge, PRIORITY_COLOR

st.set_page_config(page_title="User Management · TaskFlow", page_icon="👥", layout="wide", initial_sidebar_state="expanded")
inject_theme()
require_login()
user = get_user()

page_header("👥", "User Management", "Create, edit and manage team members")

is_admin = user["role"] == "admin"

# ======================================================
# ➕ ADD USER (ADMIN ONLY)
# ======================================================
if is_admin:
    section_header("Create New User")

    with st.expander("➕ Create New User"):
        with st.form("add_user", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            name      = col_a.text_input("Username", placeholder="e.g. john_doe")
            id_number = col_b.text_input("Employee ID", placeholder="e.g. EMP-001")
            col_c, col_d = st.columns(2)
            password  = col_c.text_input("Password", type="password", placeholder="••••••••")
            role      = col_d.selectbox("Role", ["user", "admin"])
            submitted = st.form_submit_button("➕ Create User", use_container_width=True)

    if submitted:
        if not name.strip() or not password.strip():
            st.error("Username and password are required.")
        else:
            existing = cursor.execute("SELECT id FROM users WHERE name=?", (name,)).fetchone()
            if existing:
                st.error(f"Username **{name}** already exists.")
            else:
                cursor.execute(
                    "INSERT INTO users (name, password, role, id_number) VALUES (?,?,?,?)",
                    (name.strip(), password, role, id_number.strip())
                )
                conn.commit()
                st.success(f"✅ User **{name}** created successfully!")
                st.rerun()

# ======================================================
# 📋 USERS TABLE
# ======================================================
all_users = cursor.execute("SELECT id, name, role, id_number FROM users").fetchall()
total = len(all_users)

section_header("Team Members")

# Count banner
st.markdown(f"""
<div style="display:flex;align-items:center;gap:16px;
    background:#161b22;border:1px solid #30363d;border-left:4px solid #58a6ff;
    border-radius:12px;padding:16px 22px;margin-bottom:18px;">
    <span style="font-size:2rem;">👥</span>
    <div>
        <p style="color:#8b949e;font-size:.75rem;text-transform:uppercase;letter-spacing:1px;margin:0;">Total Members</p>
        <p style="color:#e6edf3;font-size:1.8rem;font-weight:800;margin:0;">{total}</p>
    </div>
</div>
""", unsafe_allow_html=True)

if not all_users:
    st.info("No users found.")
    st.stop()

# Table header
h1, h2, h3, h4, h5 = st.columns([1, 2, 2, 0.5, 3.5])
for col, label in zip([h1,h2,h3,h4,h5],
                      ["🆔 ID No.", "👤 Username", "✉️ Role", "", "⚙️ Actions"]):
    col.markdown(f"<p style='color:#8b949e;font-size:.75rem;font-weight:600;"
                 f"text-transform:uppercase;letter-spacing:.8px;margin:0;'>{label}</p>",
                 unsafe_allow_html=True)

st.markdown("<hr style='margin:8px 0 4px;'>", unsafe_allow_html=True)

# ── Rows ──
for u in all_users:
    uid, uname, urole, uid_number = u
    display_id  = uid_number or "—"
    is_own_row  = user.get("id") == uid
    role_color  = "#f78166" if urole == "admin" else "#3fb950"
    can_edit    = is_admin or is_own_row

    c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 0.5, 3.5])
    c1.markdown(f"<span style='color:#8b949e;font-size:.85rem;'>{display_id}</span>", unsafe_allow_html=True)
    c2.markdown(f"<span style='color:#e6edf3;font-weight:600;'>{uname}</span>"
                + (" <span style='color:#58a6ff;font-size:.7rem;'>(you)</span>" if is_own_row else ""),
                unsafe_allow_html=True)
    c3.markdown(badge(urole.capitalize(), role_color), unsafe_allow_html=True)
    c4.write("")  # spacer

    with c5:
        action_col1, action_col2 = st.columns(2)
        if can_edit:
            edit_key = f"editing_{uid}"
            if action_col1.button("✏️ Edit", key=f"edit_btn_{uid}", use_container_width=True):
                st.session_state[edit_key] = True

            if st.session_state.get(edit_key):
                with st.form(key=f"edit_form_{uid}"):
                    st.markdown(f"<p style='color:#c9d1d9;font-weight:700;margin:0 0 12px;'>Edit · {uname}</p>",
                                unsafe_allow_html=True)
                    new_name      = st.text_input("New Username",  value=uname,        key=f"nn_{uid}")
                    new_id_number = st.text_input("New Employee ID", value=uid_number or "", key=f"nid_{uid}")
                    sv, cx = st.columns(2)
                    save   = sv.form_submit_button("💾 Save")
                    cancel = cx.form_submit_button("Cancel")

                if save:
                    if not new_name.strip():
                        st.error("Username cannot be empty.")
                    else:
                        dup = cursor.execute(
                            "SELECT id FROM users WHERE name=? AND id!=?", (new_name.strip(), uid)
                        ).fetchone()
                        if dup:
                            st.error("That username already exists.")
                        else:
                            cursor.execute(
                                "UPDATE users SET name=?, id_number=? WHERE id=?",
                                (new_name.strip(), new_id_number.strip(), uid)
                            )
                            conn.commit()
                            if is_own_row:
                                st.session_state["user"]["username"] = new_name.strip()
                                st.session_state["user"]["id_number"] = new_id_number.strip()
                            st.session_state[edit_key] = False
                            st.success("✅ Updated successfully!")
                            st.rerun()
                if cancel:
                    st.session_state[edit_key] = False
                    st.rerun()

        if is_admin and not is_own_row:
            if action_col2.button("🗑 Delete", key=f"del_{uid}", use_container_width=True):
                st.session_state[f"confirm_delete_{uid}"] = True

            if st.session_state.get(f"confirm_delete_{uid}"):
                st.warning(f"Permanently delete **{uname}**? All their tasks will also be removed.")
                cy, cn = st.columns(2)
                if cy.button("✅ Confirm Delete", key=f"yes_{uid}"):
                    cursor.execute("DELETE FROM users WHERE id=?", (uid,))
                    cursor.execute("DELETE FROM tasks WHERE user_id=?", (uid,))
                    conn.commit()
                    st.session_state[f"confirm_delete_{uid}"] = False
                    st.success(f"**{uname}** removed.")
                    st.rerun()
                if cn.button("Cancel", key=f"no_{uid}"):
                    st.session_state[f"confirm_delete_{uid}"] = False
                    st.rerun()

        elif not is_admin and not is_own_row:
            st.markdown("<span style='color:#8b949e;font-size:.8rem;'>🔒 No access</span>",
                        unsafe_allow_html=True)

    st.markdown("<hr style='margin:4px 0;border-color:#21262d;'>", unsafe_allow_html=True)