import sqlite3
import os

MOHINI_DB = os.environ.get(
    "MOHINI_DB",
    os.path.join(os.path.dirname(__file__), "college_records.db")
)

def get_db(MOHINI_DB):
    conn = sqlite3.connect(MOHINI_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db(MOHINI_DB)

    conn.execute('''
        CREATE TABLE IF NOT EXISTS stud (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no INTEGER NOT NULL,
            marks INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def insert_stud(name, roll_no, marks):
    conn = get_db(MOHINI_DB)

    conn.execute(
        "INSERT INTO stud (name, roll_no, marks) VALUES (?, ?, ?)",
        (name, roll_no, marks)
    )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()