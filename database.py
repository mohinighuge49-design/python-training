import sqlite3 
import os

MOHINI_DB = os.environ.get(
    "MOHINI_DB",
    os.path.join(os.path.dirname(__file__), "college_records.db")
)

# ABSOLUTE PATH -always with app.py folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOHINI_DB = os.path.join(BASE_DIR, "college_records.db")


def get_db(MOHINI_DB):
    conn = sqlite3.connect(MOHINI_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db(MOHINI_DB)

    conn.execute('''
        CREATE TABLE IF NOT EXISTS stud(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            Subject TEXT NOT NULL,
            roll_no INTEGER NOT NULL,
            marks INTEGER NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')

    try:
        conn.execute(
            "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'students'"
        )
    except Exception:
        pass

    try:
        conn.execute(
            "ALTER TABLE users ADD COLUMN email TEXT"
        )
    except Exception:
        pass

    try:
     conn.execute("ALTER TABLE stud ADD COLUMN photo TEXT")
    except Exception:
     pass

    conn.execute('''
        CREATE TABLE IF NOT EXISTS subjects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    default_subjects = [ 
        'Java',
        'C++',
        'Python',
        'Operating Systems',
        'Data Structures',
        'Database Management',
        'Computer Networks',
        'Software Engg',
        'Data analysis'
    ]

    for subject in default_subjects:
        try:
            conn.execute(
                "INSERT INTO subjects (name) VALUES (?)",
                (subject,)
            )
        except sqlite3.IntegrityError:
            pass

    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message TEXT,
            ai_reply TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        conn.execute("ALTER TABLE chat_history ADD COLUMN chat_title TEXT")
    except Exception:
        pass

    print(conn.execute(
        "SELECT * FROM chat_history LIMIT 1"
    ).fetchone())
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    conn.execute("""
        ALTER TABLE feedback
        ADD COLUMN suggestion TEXT
    """)
    conn.commit()
    conn.close()


def insert_stud(name, roll_no, Subject, marks):
    conn = get_db(MOHINI_DB)

    conn.execute(
        "INSERT INTO stud(name, roll_no, Subject, marks) VALUES (?, ?, ?, ?)",
        (name, roll_no, Subject, marks)
    )

    conn.commit()
    conn.close()

init_db()
