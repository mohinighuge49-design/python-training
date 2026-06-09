import sqlite3
from flask import Flask , url_for,redirect,render_template,conn

app=Flask (__name__)
app.secret_key='abc1234'

def get_db():
    conn= sqlite3.connect('students_records')
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    conn=get_db
    conn.execute=('''
                  CREATE TABLE IF NOT EXISTS stud(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   roll_no INTEGER NOT NULL,
                   marks INTEGER NOT NULL )
                  ''')
    
conn.commit()
conn.close()

if __name__=='__main__':
    init_db()
    app.run(debug=True)