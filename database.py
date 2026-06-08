import sqlite3
from flask import Flask, url_for, render_template, redirect, flash

app = Flask(__name__)
app.secret_key = 'abc1234567890'

def get_db():
    conn = sqlite3.connect('college_records.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

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
    app.run(debug=True)