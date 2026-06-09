from flask import Flask, render_template,request,flash,url_for,redirect
from database import get_db , init_db,MOHINI_DB

app = Flask(__name__)
app.secret_key='abc1234567890'  # Needed for flashing messages

notices_list= [
    {

        "title": "🚀python training related Notices",
        "date":    " 07 June 2026",
        "message": "💻 All students are informed that the Python Internship Program has started from 28th May 2026. ",
        "note":"The training focuses on Python programming fundamentals, problem-solving techniques,and real-world project development. ",
       "msg":"Students are encouraged to attend all sessions regularly and actively participate in practical activities to enhance their "
       "programming skills and career opportunities."
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
    conn = get_db(MOHINI_DB)

    students = conn.execute(
        "SELECT * FROM stud"
    ).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )
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
        marks = request.form["marks"]
        roll_no = request.form["roll_no"]

        if not name or not marks or not roll_no:
            flash("Please provide name, roll number and marks", "danger")
            return render_template("add_students.html")

        conn = get_db(MOHINI_DB)

        conn.execute(
            '''INSERT INTO stud (name, roll_no, marks)
               VALUES (?, ?, ?)''',
            (name, roll_no, int(marks))
        )

        conn.commit()
        conn.close()

        flash(f"Student {name} added successfully!", "success")

        return redirect(url_for("add_student"))

    return render_template("add_students.html")
@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db(MOHINI_DB)

    conn.execute(
        "DELETE FROM stud WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Student deleted successfully!", "success")

    return redirect(url_for('students'))
    
if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)                                                                                                                                                    