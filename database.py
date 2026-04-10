import sqlite3

# ---------------- CONNECT DATABASE ----------------
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

# ---------------- USERS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

# ---------------- TASKS TABLE ----------------
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
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
# ---------------- ATTENDANCE TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    check_in TEXT,
    check_out TEXT,
    status TEXT,
    leave_reason TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")


# ---------------- ADD MISSING COLUMNS (SAFE UPDATE) ----------------
def add_column_if_not_exists(column, definition):

    cursor.execute("PRAGMA table_info(tasks)")
    columns = [col[1] for col in cursor.fetchall()]

    if column not in columns:
        cursor.execute(f"ALTER TABLE tasks ADD COLUMN {column} {definition}")

add_column_if_not_exists("main_task", "TEXT")
add_column_if_not_exists("sub_task", "TEXT")
add_column_if_not_exists("priority", "TEXT")
add_column_if_not_exists("start_date", "TEXT")
add_column_if_not_exists("end_date", "TEXT")
add_column_if_not_exists("completed", "INTEGER DEFAULT 0")
add_column_if_not_exists("completed_at", "TEXT")
add_column_if_not_exists("time_in", "TEXT")
add_column_if_not_exists("time_out", "TEXT")
add_column_if_not_exists("status", "TEXT")       # Present / Leave
add_column_if_not_exists("leave_reason", "TEXT")


conn.commit()