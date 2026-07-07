from flask import Flask, jsonify, render_template, request, flash, url_for, redirect,session
from database import get_db, init_db, MOHINI_DB
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from flask import Response


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

@app.route('/dbpath')
def dbpath():
    return MOHINI_DB

@app.route('/college_info')
def college_info():
    return render_template('college_info.html')

@app.route('/notices')
def notices():
    return render_template('notices.html', notices=notices_list)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db(MOHINI_DB)

    total_students = conn.execute(
        "SELECT COUNT(*) FROM stud"
    ).fetchone()[0]

    total_Subject = conn.execute(
        "SELECT COUNT(DISTINCT Subject) FROM stud"
    ).fetchone()[0]

    pass_count = conn.execute(
        "SELECT COUNT(*) FROM stud WHERE marks >= 35"
    ).fetchone()[0]

    fail_count = conn.execute(
        "SELECT COUNT(*) FROM stud WHERE marks < 35"
    ).fetchone()[0]

    avg_marks = conn.execute(
        "SELECT ROUND(AVG(marks),2) FROM stud"
    ).fetchone()[0]

    topper = conn.execute(
        "SELECT name, marks FROM stud ORDER BY marks DESC LIMIT 1"
    ).fetchone()

    pass_percentage = 0
    if total_students > 0:
        pass_percentage = round(
            (pass_count / total_students) * 100, 2
        )

    top_students = conn.execute(
        """
        SELECT name, marks
        FROM stud
        ORDER BY marks DESC
        LIMIT 5
        """
    ).fetchall()

    best_subject = conn.execute(
    """
    SELECT Subject,
           ROUND(AVG(marks),2) as avg_marks
    FROM stud
    GROUP BY Subject
    ORDER BY avg_marks DESC
    LIMIT 1
    """
).fetchone()

    recent_students = conn.execute(
    """
    SELECT name, Subject, marks
    FROM stud
    ORDER BY id DESC
    LIMIT 5
    """
).fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        total_students=total_students,
        total_Subject=total_Subject,
        pass_count=pass_count,
        fail_count=fail_count,
        avg_marks=avg_marks,
        top_students=top_students,
        recent_students=recent_students,
        topper=topper,
        best_subject=best_subject,
        pass_percentage=pass_percentage
    )


#...........Export.............

@app.route('/export')
def export_data():

    conn = get_db(MOHINI_DB)

    students = conn.execute(
        "SELECT * FROM stud"
    ).fetchall()

    conn.close()

    def generate():
        data = csv.writer(
            open('temp.csv', 'w', newline='')
        )

    output = []

    output.append("ID,Name,Roll No,Subject,Marks\n")

    for student in students:
        output.append(
            f"{student['id']},"
            f"{student['name']},"
            f"{student['roll_no']},"
            f"{student['Subject']},"
            f"{student['marks']}\n"
        )

    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=students.csv"
        }
    )


#============add_students==========

@app.route("/add_students", methods=["GET", "POST"])
def add_student():
    if session.get('role') !='admin':
        flash("Admins only..! You do not have permission","danger")
        return redirect(url_for('home'))
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

#=========FILTER ROUTE==========

@app.route('/filter')
def filter_students():
   
    subject = request.args.get('subject', '')
    grade = request.args.get('grade', '')

    conn = get_db(MOHINI_DB)
    
    subjects = conn.execute('''SELECT DISTINCT Subject FROM stud
                            WHERE subject IS NOT NULL
                            AND subject != ""
                            ORDER BY subject ASC''').fetchall()    
    
    query = 'SELECT * FROM stud WHERE 1=1'
    params = []
    if subject:
      query += ' AND Subject = ?'
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


#========filter===========
@app.route('/students')
def students():

    if 'username' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '')
    conn = get_db(MOHINI_DB)

    if search:
        students = conn.execute(
            "SELECT * FROM stud WHERE name LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    else:
        students = conn.execute(
            "SELECT * FROM stud"
        ).fetchall()

    conn.close()

    return render_template(
        'students.html',
        students=students
    )

#==========students_details (view)==============
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

#=========edit_student  (update)===========
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
   if session.get('role') !='admin':
        flash("Admins only..! You do not have permission","danger")
        return redirect(url_for('home'))
  
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

#==========delete_student  (delete)===========
@app.route('/delete/<int:id>')
def delete_student(id):
    if session.get('role') !='admin':
        flash("Admins only..! You do not have permission","danger")
        return redirect(url_for('home'))
    conn = get_db(MOHINI_DB)
 
    conn.execute("DELETE FROM stud WHERE id=?", (id,))

    conn.commit()
    conn.close()

    flash("Student deleted successfully!", "success")
    return redirect(url_for('students'))

#======REGISTER, LOGIN ,LOGOUT=========
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed = generate_password_hash(password)

        conn = get_db(MOHINI_DB)

        existing_user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:
            flash("Username already exists!", "danger")
            return redirect('/register')

        conn.execute(
            '''
            INSERT INTO users
            (username,email,password,role)
            VALUES (?,?,?,?)
            ''',
            (username,email,hashed,'student')
        )

        conn.commit()
        conn.close()

        flash("Registration Successful!", "success")
        return redirect('/login')

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

      
        conn = get_db(MOHINI_DB)
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['email'] = user['email']
            session['role'] = user['role']
            flash(f'Welcome {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():

    session.pop('username', None)
    session.pop('role',None)
    flash("You have been logged out..!", "info")

    return redirect(url_for('login'))

#==========PROFILE PAGE , SETTINGS , AND EDIT PROFILE============

@app.route('/profile')
def profile():
    if not session.get('username'):
        return redirect('/login')
    return render_template('profile.html')


@app.route('/settings')
def settings():
    if not session.get('username'):
        return redirect('/login')
    return render_template('settings.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('username'):
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # ⚠️ Example: store in session (you can save in DB later)
        session['name'] = name
        session['email'] = email

        flash("Profile updated successfully!", "success")
        return redirect('/profile')

    return render_template('edit_profile.html')

@app.route('/subjects')
def subjects():
    conn= get_db(MOHINI_DB)
    rows = conn.execute('''
            SELECT subjects.name AS subject_name, COUNT(stud.id) AS student_count
            FROM subjects
            LEFT JOIN stud ON stud.subject = subjects.name
            GROUP BY subjects.name
            ORDER BY subjects.name
    ''').fetchall()
    conn.close()
    return render_template('subjects.html', rows=rows)

@app.route('/check')
def check():
    conn = get_db(MOHINI_DB)

    rows = conn.execute("PRAGMA table_info(stud)").fetchall()

    result = []
    for row in rows:
        result.append(dict(row))

    conn.close()
    return str(result)

    from flask import jsonify, request


@app.route('/assistant')
def assistant():
    return render_template('assistant.html')

    #============================chatboat route==============================
@app.route('/chatbot', methods=['POST'])
def chatbot():

    message = request.form.get('message', '').lower().strip()

    conn = get_db(MOHINI_DB)

    # ---------------- SMART KEYWORD MATCH ---------------- #

    
    responses = {

        # ================= GREETINGS =================
        "hello": "👋 Hello Student! How can I help you?",
        "hi": "👋 Hi! Ask me about college, students, marks, subjects.",
        "good morning": "🌅 Good Morning! Ready to learn?",
        "good night": "🌙 Good Night! Take rest 😊",
        "ok": "👍 Okay! What else do you want to know?",
        "bye": "👋 Goodbye! See you soon.",
        "thanks": "🙏 You're welcome! Happy to help.",
        "thank you": "🙏 You're welcome! Happy to help.",
        "ohk": "👍 Okay! What else do you want to know?",
        "done": "✅ Great! Anything else you want to ask?",
        "welcome": "🙏 You're welcome! Happy to help.",
        "good": "👍 Great! Keep up the good work.",

        # ================= COLLEGE INFO =================
        "college": "🏫 Government Polytechnic Hingoli is a technical institute.",
        "about college": "🏫 It provides diploma courses in engineering fields.",
        "database": "🗄️ Database is connected to student management system.",

        # ================= HELP =================
        "help": "🤖 Try: students, topper, average, subjects, recent, marks",

        # ================= STUDENTS =================
        "students": lambda: f"👨‍🎓 Total Students: {conn.execute('SELECT COUNT(*) as c FROM stud').fetchone()['c']}",
        "total students": lambda: f"👨‍🎓 Total Students: {conn.execute('SELECT COUNT(*) as c FROM stud').fetchone()['c']}",
        "count students": lambda: f"👨‍🎓 Total Students: {conn.execute('SELECT COUNT(*) as c FROM stud').fetchone()['c']}",

        "show students": lambda: (
            "👨‍🎓 Students List:\n" +
            "\n".join([i["name"] for i in conn.execute("SELECT name FROM stud").fetchall()])
        ),

        # ================= TOPPER =================
        "topper": lambda: (
            lambda r: f"🏆 Topper: {r['name']} with {r['marks']} marks"
        )(conn.execute("SELECT name, marks FROM stud ORDER BY marks DESC LIMIT 1").fetchone()),

        "highest marks": lambda: f"🏆 Highest Marks: {conn.execute('SELECT MAX(marks) as m FROM stud').fetchone()['m']}",

        "lowest marks": lambda: f"📉 Lowest Marks: {conn.execute('SELECT MIN(marks) as m FROM stud').fetchone()['m']}",

        # ================= AVERAGE =================
        "average": lambda: (
            lambda r: f"📊 Average Marks: {round(r['avg'],2)}"
        )(conn.execute("SELECT AVG(marks) as avg FROM stud").fetchone()),

        # ================= RECENT =================
        "recent": lambda: (
            "🕒 Recent Students: " +
            ", ".join([i["name"] for i in conn.execute("SELECT name FROM stud ORDER BY id DESC LIMIT 5").fetchall()])
        ),

        # ================= SUBJECTS =================
        "subjects": lambda: (
            "📚 Subjects: " +
            ", ".join([i["name"] for i in conn.execute("SELECT name FROM subjects").fetchall()])
        ),

        # ================= PASS / FAIL =================
        "pass students": lambda: f"✅ Passed Students: {conn.execute('SELECT COUNT(*) as c FROM stud WHERE marks >= 40').fetchone()['c']}",
        "fail students": lambda: f"❌ Failed Students: {conn.execute('SELECT COUNT(*) as c FROM stud WHERE marks < 40').fetchone()['c']}",

        # ================= EXTRA SMART =================
        "marks": "📊 Try: topper, average marks, highest marks, lowest marks",

        "student list": lambda: (
            "👨‍🎓 All Students:\n" +
            "\n".join([i["name"] for i in conn.execute("SELECT name FROM stud").fetchall()])
        ),

        "top 5": lambda: (
            "🏅 Top 5 Students:\n" +
            "\n".join(
                [f"{i['name']} - {i['marks']}" for i in conn.execute(
                    "SELECT name, marks FROM stud ORDER BY marks DESC LIMIT 5"
                ).fetchall()]
            )
        ),

        "attendance": "📅 Attendance system is coming soon in next update!",

        "result": "📊 Ask: topper, average, pass students, fail students"
    }
    reply = None

    # ---------------- SMART SEARCH ---------------- #
    for key in responses:
        if key in message:
            result = responses[key]
            reply = result() if callable(result) else result
            break

    # ---------------- DEFAULT AI RESPONSE ---------------- #
    if not reply:
        if "marks" in message:
            reply = "📊 You can ask: topper, average marks, or student details."
        elif "name" in message:
            reply = "👨‍🎓 Try: show students or recent students."
        else:
            reply = "🤖 Sorry, I didn't understand. Try asking about students, topper, marks, subjects."

    conn.close()

    return jsonify({"reply": reply})
init_db()
if __name__ == "__main__":
    
    app.run(debug=True)