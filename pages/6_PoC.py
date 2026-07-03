import streamlit as st
import pandas as pd
from io import BytesIO
# -------------------------------------------------
# PoC (Proof of Concept) entry page
# -------------------------------------------------
st.set_page_config(page_title="PoC Entries", page_icon="💡", layout="wide")

# Initialise the DataFrame in session state if not present
if "poc_table" not in st.session_state:
    st.session_state["poc_table"] = pd.DataFrame(
        columns=[
            "Mentor Name",
            "Intern",
            "Use Case",
            "Primary Users",
            "Expected ROI",
            "Production Level",
            "GitHub Link",
        ]
    )

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
        }
        # If an entry with the same Intern already exists, update that row instead of adding duplicate
        if not st.session_state["poc_table"].empty and intern in st.session_state["poc_table"]["Intern"].values:
            idx = st.session_state["poc_table"][st.session_state["poc_table"]["Intern"] == intern].index[0]
            for key, val in new_row.items():
                if val:  # only replace non‑empty values
                    st.session_state["poc_table"].at[idx, key] = val
            st.success(f"Entry for intern '{intern}' updated!")
        else:
            st.session_state["poc_table"] = pd.concat([st.session_state["poc_table"], pd.DataFrame([new_row])], ignore_index=True)
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
        df = st.session_state["poc_table"]
        st.session_state["poc_table"] = df[~df["Intern"].isin(interns_to_delete)].reset_index(drop=True)
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
