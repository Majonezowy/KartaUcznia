import sqlite3
from datetime import datetime

# Database connection
DATABASE_PATH = "./db.sqlite"
con = sqlite3.connect(DATABASE_PATH)
cur = con.cursor()

# Create tables if they don't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number VARCHAR(128),
    imie VARCHAR(255),
    nazwisko VARCHAR(255),
    user_type VARCHAR(50) CHECK(user_type IN ('student', 'teacher')) NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS niepytajki (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    niepytajka TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# Helper function for querying user data
def get_user(serial_number):
    cur.execute("SELECT * FROM users WHERE serial_number = ?", (serial_number,))
    return cur.fetchone()

# Helper function for checking if student exists
def get_student_id(serial_number):
    cur.execute("""
        SELECT id FROM users WHERE serial_number = ? AND user_type = 'student'
    """, (serial_number,))
    return cur.fetchone()

# Get user type
def get_user_type(serial_number):
    user = get_user(serial_number)
    return user[4] if user else None

# Get student niepytajki
def get_students_niepytajki(serial_number):
    student_id = get_student_id(serial_number)
    if student_id:
        cur.execute("""
            SELECT * FROM niepytajki WHERE student_id = ?
        """, (student_id[0],))
        return cur.fetchall()
    return []

# Check if niepytajka is used today
def check_if_niepytajka_used_today(serial_number):
    student_id = get_student_id(serial_number)
    if student_id:
        cur.execute("""
            SELECT 1 FROM niepytajki
            WHERE student_id = ? AND used IS NOT NULL AND DATE(used) = DATE('now')
        """, (student_id[0],))
        return cur.fetchone() is not None
    return False

# Mark niepytajka as used
def mark_niepytajka_as_used(serial_number):
    student_id = get_student_id(serial_number)
    if not student_id:
        return 0

    # Clean up old used niepytajki
    cur.execute("""
        DELETE FROM niepytajki WHERE student_id = ? AND used IS NOT NULL AND DATE(used) < DATE('now')
    """, (student_id[0],))
    con.commit()

    # If already used today, return status 2
    if check_if_niepytajka_used_today(serial_number):
        return 2

    # Find an unused niepytajka and mark it as used
    cur.execute("""
        SELECT niepytajka FROM niepytajki 
        WHERE student_id = ? AND used IS NULL LIMIT 1
    """, (student_id[0],))
    niepytajka = cur.fetchone()

    if niepytajka:
        cur.execute("""
            UPDATE niepytajki SET used = DATE('now') WHERE niepytajka = ?
        """, (niepytajka[0],))
        con.commit()
        return 1

    return 0

# Assign niepytajka to student
def assign_niepytajka_to_student(serial_number, niepytajka_text):
    student_id = get_student_id(serial_number)
    if student_id:
        cur.execute("""
            INSERT INTO niepytajki (student_id, niepytajka)
            VALUES (?, ?)
        """, (student_id[0], niepytajka_text))
        con.commit()
        return True
    return False
