import sqlite3
import os

MOHINI_DB = os.environ.get(
    "MOHINI_DB",
    os.path.join(os.path.dirname(__file__), "college_records.db")
)

def get_db(MOHINI):
    
    conn = sqlite3.connect(MOHINI)
    conn.row_factory = sqlite3.Row
    return conn
''' import sqlite3
from flask import Flask
app = Flask(__name__)
app.secret_key = 'abc1234567890'

def get_db():
    conn = sqlite3.connect('college_records.db')
    conn.row_factory = sqlite3.Row
    return conn
'''
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

if __name__ == '__main__':
    init_db()
   