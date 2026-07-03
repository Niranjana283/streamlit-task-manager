import streamlit as st
import pandas as pd
from io import BytesIO
from database import add_poc_entry_multi, get_all_poc_entries_multi, delete_poc_entry_multi_by_intern

# -------------------------------------------------
# PoC (Proof of Concept) entry page
# -------------------------------------------------
st.set_page_config(page_title="PoC Entries", page_icon="💡", layout="wide")

# Initialise the DataFrame in session state if not present
if "poc_table" not in st.session_state:
    # Load persisted entries from the multi‑entry table (or start empty)
    df = get_all_poc_entries_multi()
    if not df.empty:
        df = df.rename(columns={
            "mentor_name": "Mentor Name",
            "intern": "Intern",
            "use_case": "Use Case",
            "primary_users": "Primary Users",
            "expected_roi": "Expected ROI",
            "production_level": "Production Level",
            "github_link": "GitHub Link",
            "features": "Features",
            "function": "Function",
        })
    else:
        df = pd.DataFrame(
            columns=[
                "Mentor Name",
                "Intern",
                "Use Case",
                "Primary Users",
                "Expected ROI",
                "Production Level",
                "GitHub Link",
                "Features",
                "Function",
            ]
        )
    st.session_state["poc_table"] = df

st.title("💡 PoC – Add & Export Entries")
st.write(
    "Use the form below to record a new Proof‑of‑Concept entry. "
    "All entries are stored for the current session and can be exported as CSV."
)

# -------------------------------------------------------------------
# Form to add a new row
# -------------------------------------------------------------------
with st.form("poc_form"):
    mentor = st.text_input("Mentor Name")
    # Intern selection – dropdown of existing interns with option to add new
    existing_interns = list(st.session_state["poc_table"]["Intern"].unique()) if "poc_table" in st.session_state else []
    intern_options = ["<Add new>"] + existing_interns
    intern_choice = st.selectbox("Intern", intern_options)
    if intern_choice == "<Add new>":
        intern = st.text_input("Intern (new)")
    else:
        intern = intern_choice
    use_case = st.text_input("Use Case")
    primary_users = st.text_input("Primary Users")
    expected_roi = st.text_input("Expected ROI")
    production_level = st.text_input("Production Level")
    github_link = st.text_input("GitHub Link")
    features = st.text_input("Features")
    function = st.text_input("Function")
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        # Prepare new row data
        new_row = {
            "Mentor Name": mentor,
            "Intern": intern,
            "Use Case": use_case,
            "Primary Users": primary_users,
            "Expected ROI": expected_roi,
            "Production Level": production_level,
            "GitHub Link": github_link,
            "Features": features,
            "Function": function,
        }
        # Persist the new entry in the database (allows duplicate interns)
        add_poc_entry_multi(new_row)
        # Refresh the session table from the DB and rename columns for UI
        df = get_all_poc_entries_multi()
        df = df.rename(columns={
            "mentor_name": "Mentor Name",
            "intern": "Intern",
            "use_case": "Use Case",
            "primary_users": "Primary Users",
            "expected_roi": "Expected ROI",
            "production_level": "Production Level",
            "github_link": "GitHub Link",
            "features": "Features",
        })
        st.session_state["poc_table"] = df
        st.success("Entry added!")

# -------------------------------------------------------------------
# Display the table (spreadsheet‑like view)
# -------------------------------------------------------------------
st.subheader("Current PoC Entries")
if st.session_state["poc_table"].empty:
    st.info("No entries yet. Add one using the form above.")
else:
    # Show DataFrame as an interactive grid
    st.dataframe(st.session_state["poc_table"])
    # Delete selected rows via multiselect
    interns_to_delete = st.multiselect(
        "Select Intern(s) to delete",
        options=st.session_state["poc_table"]["Intern"].unique(),
        key="delete_select"
    )
    if st.button("🗑️ Delete Selected", key="delete_button") and interns_to_delete:
        for intern in interns_to_delete:
            delete_poc_entry_multi_by_intern(intern)
        # Reload table from DB after deletions and rename columns
        df = get_all_poc_entries_multi()
        df = df.rename(columns={
            "mentor_name": "Mentor Name",
            "intern": "Intern",
            "use_case": "Use Case",
            "primary_users": "Primary Users",
            "expected_roi": "Expected ROI",
            "production_level": "Production Level",
            "github_link": "GitHub Link",
            "features": "Features",
        })
        st.session_state["poc_table"] = df
        st.success(f"Deleted {len(interns_to_delete)} entry(ies).")
        st.rerun()

# -------------------------------------------------------------------
# Export button – Excel download (Excel‑style sheet)
# -------------------------------------------------------------------
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    st.session_state["poc_table"].to_excel(writer, index=False, sheet_name="PoC Entries")
excel_bytes = excel_buffer.getvalue()
st.download_button(
    label="📥 Export as Excel",
    data=excel_bytes,
    file_name="poc_entries.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
