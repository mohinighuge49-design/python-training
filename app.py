

from flask import Flask, render_template, request, flash, url_for, redirect
from database import get_db, init_db, MOHINI_DB

app = Flask(__name__)
app.secret_key = 'abc1234567890'

notices_list = [
    {
        "title": "🚀python training related Notices",
        "message": "Python Internship Program started.",
        "note": "Training focuses on Python fundamentals.",
        "msg": "Students should attend regularly."
    }
]

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/college_info')
def college_info():
    return render_template('college_info.html')


@app.route('/students')
def students():
    search = request.args.get('search', '')
    conn = get_db(MOHINI_DB)

    if search:
        students = conn.execute(
            "SELECT * FROM stud WHERE name LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM stud").fetchall()

    conn.close()
    return render_template('students.html', students=students)


@app.route('/notices')
def notices():
    return render_template('notices.html', notices=notices_list)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/add_students", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        Subject = request.form["Subject"]
        marks = request.form["marks"]

        if not name or not roll_no or not Subject or not marks:
            flash("Please provide all fields", "danger")
            return render_template("add_students.html")

        conn = get_db(MOHINI_DB)

        conn.execute(
            "INSERT INTO stud(name, roll_no, Subject, marks) VALUES (?,?,?,?)",
            (name, roll_no, Subject, marks)
        )

        conn.commit()
        conn.close()

        flash(f"{name} added successfully!", "success")
        return redirect(url_for("students"))

    return render_template("add_students.html")


@app.route("/students_details/<int:id>")
def detail(id):

    conn = get_db(MOHINI_DB)

    student = conn.execute(
        "SELECT * FROM stud WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        flash("Student not found!", "danger")
        return redirect(url_for("students"))

    return render_template("detail.html", student=student)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    conn = get_db(MOHINI_DB)

    if request.method == 'POST':

        name = request.form['name']
        roll_no = request.form['roll_no']
        Subject = request.form['Subject']
        marks = request.form['marks']

        conn.execute(
            "UPDATE stud SET name=?, roll_no=?, Subject=?, marks=? WHERE id=?",
            (name, roll_no, Subject, marks, id)
        )

        conn.commit()
        conn.close()

        flash("Student updated successfully!", "success")
        return redirect(url_for('students'))

    student = conn.execute(
        "SELECT * FROM stud WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template('edit_students.html', student=student)


@app.route('/delete/<int:id>')
def delete_student(id):

    conn = get_db(MOHINI_DB)

    conn.execute("DELETE FROM stud WHERE id=?", (id,))

    conn.commit()
    conn.close()

    flash("Student deleted successfully!", "success")
    return redirect(url_for('students'))


# =========================
# 🔥 FILTER ROUTE FIXED
# =========================
@app.route('/filter')
def filter_students():
    #Values from URL
    subject = request.args.get('subject', '')
    grade = request.args.get('grade', '')

    conn = get_db(MOHINI_DB)
    # Unique subjects for dropdown
    subjects = conn.execute('''SELECT DISTINCT Subject FROM stud
                            WHERE subject IS NOT NULL
                            AND subject != ""
                            ORDER BY subject ASC''').fetchall()    
    
    #Dynamic query- WHERE 1=1
    query = 'SELECT * FROM stud WHERE 1=1'
    params = []
    if subjects:
        query += ' AND subject = ?'
        params.append(subject)
    if grade =='excellent':
        query += ' AND marks >= 90'
    elif grade == 'good':
        query += ' AND marks >= 75 AND marks < 90'
    elif grade == 'average':
        query += ' AND marks >= 60 AND marks < 75'
    elif grade == 'poor':
        query += ' AND marks < 45'
        
    query += ' ORDER BY id DESC'
    students = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('filter.html', students=students, subjects=subjects, selected_subject=subject, selected_grade=grade)



if __name__ == "__main__":
    init_db()
    app.run(debug=True)