import sqlite3

# ================= CONNECT DATABASE =================
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")


# ================= USERS TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user'
)
""")


# ================= TASKS TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    main_task TEXT,
    sub_task TEXT,
    priority TEXT,
    start_date TEXT,
    end_date TEXT,
    completed INTEGER DEFAULT 0,
    completed_at TEXT,
    time_in TEXT,
    time_out TEXT,
    status TEXT,
    leave_reason TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")


# ================= ATTENDANCE TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    check_in TEXT,
    check_out TEXT,
    status TEXT,
    leave_reason TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")


conn.commit()


# ================= AUTO MIGRATION SYSTEM =================
def add_column_if_missing(table, column, column_type):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cursor.fetchall()]

    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
        conn.commit()
        print(f"Added {column} to {table}")


# Run migrations
add_column_if_missing("users", "password", "TEXT")
add_column_if_missing("users", "role", "TEXT DEFAULT 'user'")
add_column_if_missing("users", "id_number", "TEXT")
add_column_if_missing("tasks", "due_date", "TEXT")

# ================= PO C TABLE =================
# Ensure PoC table exists without dropping existing data
cursor.execute("""
CREATE TABLE IF NOT EXISTS poc_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_name TEXT,
    intern TEXT,
    use_case TEXT,
    primary_users TEXT,
    expected_roi TEXT,
    production_level TEXT,
    github_link TEXT,
    features TEXT,
    function TEXT,
    url TEXT
)
""")


# Helper functions for PoC entries

def add_poc_entry(entry):
    """Insert a new PoC entry into the unique‑intern table."""
    cursor.execute(
        """INSERT INTO poc_entries (mentor_name, intern, use_case, primary_users, expected_roi, production_level, github_link, features, function, url)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            entry.get("Mentor Name"),
            entry.get("Intern"),
            entry.get("Use Case"),
            entry.get("Primary Users"),
            entry.get("Expected ROI"),
            entry.get("Production Level"),
            entry.get("GitHub Link"),
            entry.get("Features"),
            entry.get("Function"),
            entry.get("URL"),
        ),
    )
    conn.commit()

def get_all_poc_entries():
    """Return a DataFrame from the unique‑intern table."""
    import pandas as pd
    return pd.read_sql_query("SELECT * FROM poc_entries", conn)

def update_poc_entry_by_intern(intern, updated):
    """Update an existing entry identified by `intern`."""
    cursor.execute(
        """UPDATE poc_entries SET mentor_name = ?, use_case = ?, primary_users = ?, expected_roi = ?, production_level = ?, github_link = ?, features = ?, function = ?
           WHERE intern = ?""",
        (
            updated.get("Mentor Name"),
            updated.get("Use Case"),
            updated.get("Primary Users"),
            updated.get("Expected ROI"),
            updated.get("Production Level"),
            updated.get("GitHub Link"),
            updated.get("Features"),
            updated.get("Function"),
            intern,
        ),
    )
    conn.commit()

def update_poc_entry(entry_id, updated):
    """Update an existing entry identified by `id`."""
    cursor.execute(
        """UPDATE poc_entries SET mentor_name = ?, intern = ?, use_case = ?, primary_users = ?, expected_roi = ?, production_level = ?, github_link = ?, features = ?, function = ?, url = ?
           WHERE id = ?""",
        (
            updated.get("Mentor Name"),
            updated.get("Intern"),
            updated.get("Use Case"),
            updated.get("Primary Users"),
            updated.get("Expected ROI"),
            updated.get("Production Level"),
            updated.get("GitHub Link"),
            updated.get("Features"),
            updated.get("Function"),
            updated.get("URL"),
            entry_id,
        ),
    )
    conn.commit()

def delete_poc_entry(entry_id):
    """Delete a PoC entry by its primary key id."""
    cursor.execute("DELETE FROM poc_entries WHERE id = ?", (entry_id,))
    conn.commit()

# Multi-entry helper functions and migrations removed; using unified poc_entries table
# Run migration for PoC table columns (if needed)
add_column_if_missing("poc_entries", "mentor_name", "TEXT")
add_column_if_missing("poc_entries", "intern", "TEXT")
add_column_if_missing("poc_entries", "use_case", "TEXT")
add_column_if_missing("poc_entries", "primary_users", "TEXT")
add_column_if_missing("poc_entries", "expected_roi", "TEXT")
add_column_if_missing("poc_entries", "production_level", "TEXT")
add_column_if_missing("poc_entries", "github_link", "TEXT")
add_column_if_missing("poc_entries", "features", "TEXT")
add_column_if_missing("poc_entries", "function", "TEXT")
add_column_if_missing("poc_entries", "url", "TEXT")

