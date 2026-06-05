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
        print(f"✅ Added {column} to {table}")


# Run migrations
add_column_if_missing("users", "password", "TEXT")
add_column_if_missing("users", "role", "TEXT DEFAULT 'user'")
add_column_if_missing("users", "id_number", "TEXT")