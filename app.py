from email import message
import smtplib
from email.message import EmailMessage
from re import search
from turtle import title
import uuid
from click import prompt
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, flash, url_for, redirect, session, abort
from database import get_db, init_db, MOHINI_DB
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import csv
from flask import Response
from groq import Groq
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

app = Flask(__name__)
app.secret_key = 'abc1234567890'

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


notices_list = [

    {
        "title": "Semester Examination Schedule",
        "message": "The semester examination timetable has been announced.",
        "note": "Students are requested to check the examination schedule carefully.",
        "msg": "Contact your department for any queries.",
        "priority": "Urgent",
        "pinned": True,
        "expiry": "20 Aug 2026"
    },

    {
        "title": "Python Workshop",
        "message": "A Python programming workshop will be conducted for students.",
        "note": "All interested students are encouraged to participate.",
        "msg": "Venue: Computer Department Lab.",
        "priority": "Important",
        "pinned": False,
        "expiry": "25 Aug 2026"
    },

    {
        "title": "College Holiday",
        "message": "The college will remain closed on the upcoming holiday.",
        "note": "Regular classes will resume from the next working day.",
        "msg": "",
        "priority": "General",
        "pinned": False,
        "expiry": "18 Aug 2026"
    }

]
@app.route('/')
def home():

    conn = get_db(MOHINI_DB)

    # Dashboard Cards
    total_students = conn.execute(
        "SELECT COUNT(*) FROM stud"
    ).fetchone()[0]

    total_subjects = conn.execute(
        "SELECT COUNT(DISTINCT Subject) FROM stud"
    ).fetchone()[0]

    pass_count = conn.execute(
        "SELECT COUNT(*) FROM stud WHERE marks >= 40"
    ).fetchone()[0]

    fail_count = conn.execute(
        "SELECT COUNT(*) FROM stud WHERE marks < 35"
    ).fetchone()[0]

    pass_percentage = round((pass_count / total_students) * 100, 2) if total_students else 0

    avg_marks = conn.execute(
        "SELECT ROUND(AVG(marks),2) FROM stud"
    ).fetchone()[0]

    topper = conn.execute(
        "SELECT * FROM stud ORDER BY marks DESC LIMIT 1"
    ).fetchone()

    best_subject = conn.execute("""
        SELECT Subject,
               ROUND(AVG(marks),2) AS avg_marks
        FROM stud
        GROUP BY Subject
        ORDER BY avg_marks DESC
        LIMIT 1
    """).fetchone()

    top_students = conn.execute("""
        SELECT * FROM stud
        ORDER BY marks DESC
        LIMIT 5
    """).fetchall()

    recent_students = conn.execute("""
        SELECT * FROM stud
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "home.html",
        total_students=total_students,
        total_subjects=total_subjects,
        pass_count=pass_count,
        fail_count=fail_count,
        pass_percentage=pass_percentage,
        avg_marks=avg_marks,
        topper=topper,
        best_subject=best_subject,
        top_students=top_students,
        recent_students=recent_students
    )

@app.route('/college_info')
def college_info():
    return render_template('college_info.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/notices')
def notices():

    priority_order = {
        "Urgent": 1,
        "Important": 2,
        "General": 3
    }

    sorted_notices = sorted(
        notices_list,
        key=lambda notice: (
            not notice.get("pinned", False),
            priority_order.get(
                notice.get("priority", "General"),
                3
            )
        )
    )

    return render_template(
        'notices.html',
        notices=sorted_notices
    )
@app.route('/delete_notice/<int:id>')
def delete_notice(id):

    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()

    db.execute(
        "DELETE FROM notices WHERE id = ?",
        (id,)
    )

    db.commit()

    flash("Notice deleted successfully!", "success")

    return redirect(url_for('notices'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        try:

            msg = EmailMessage()

            msg['Subject'] = f"College Smart Portal - {subject}"
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = EMAIL_ADDRESS
            msg['Reply-To'] = email

            msg.set_content(f"""
New Contact Message

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
""")

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:

                smtp.login(
                    os.getenv('EMAIL_ADDRESS'),
                    os.getenv('EMAIL_PASSWORD')
                )

                smtp.send_message(msg)

            flash('✅ Message sent successfully!', 'success')

        except Exception as e:

            print('EMAIL ERROR:', e)

            flash(
                '❌ Message could not be sent.',
                'danger'
            )

        return redirect(url_for('contact_us'))

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

    print("Total Students:", total_students)
    print("Pass Count:", pass_count)
    print("Fail Count:", fail_count)
    print("Pass Percentage:", pass_percentage)
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

    if session.get('role') != 'admin':
        flash("Admins only..! You do not have permission", "danger")
        return redirect(url_for('home'))

    if request.method == "POST":

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        Subject = request.form["Subject"]
        marks = request.form["marks"]

        # Photo Upload
        photo = request.files.get("photo")

        filename = "default.png"

        if photo and photo.filename != "":

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        if not name or not roll_no or not Subject or not marks:
            flash("Please provide all fields", "danger")
            return render_template("add_students.html")

        conn = get_db(MOHINI_DB)

        conn.execute(
            """
            INSERT INTO stud
            (name, roll_no, Subject, marks, photo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, roll_no, Subject, marks, filename)
        )

        conn.commit()
        conn.close()

        flash(f"{name} added successfully!", "success")

        return redirect(url_for("students"))

    return render_template("add_students.html")

    # ============ REPORT CARD ============

@app.route('/report_card/<int:student_id>')
def report_card(student_id):

    conn = get_db(MOHINI_DB)

    student = conn.execute(
        "SELECT * FROM stud WHERE id=?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        flash("Student not found!", "danger")
        return redirect(url_for('students'))

    # Grade calculation
    marks = student['marks']

    if marks >= 90:
        grade = "A+"
    elif marks >= 80:
        grade = "A"
    elif marks >= 70:
        grade = "B+"
    elif marks >= 60:
        grade = "B"
    else:
        grade = "C"

    result = "PASS" if marks >= 35 else "FAIL"


    return render_template(
        "report_card.html",
        student=student,
        grade=grade,
        result=result
    )

#=========FILTER ROUTE==========

@app.route('/filter')
def filter_students():

    subject = request.args.get('subject', '')
    grade = request.args.get('grade', '')

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    conn = get_db(MOHINI_DB)

    # Subjects
    subjects = conn.execute('''
        SELECT DISTINCT Subject
        FROM stud
        WHERE Subject IS NOT NULL
        AND Subject != ""
        ORDER BY Subject ASC
    ''').fetchall()

    # Main query
    query = 'SELECT * FROM stud WHERE 1=1'
    count_query = 'SELECT COUNT(*) FROM stud WHERE 1=1'

    params = []
    count_params = []

    # Subject filter
    if subject:
        query += ' AND Subject = ?'
        count_query += ' AND Subject = ?'

        params.append(subject)
        count_params.append(subject)

    # Grade filter
    if grade == 'excellent':
        query += ' AND marks >= 90'
        count_query += ' AND marks >= 90'

    elif grade == 'good':
        query += ' AND marks >= 75 AND marks < 90'
        count_query += ' AND marks >= 75 AND marks < 90'

    elif grade == 'average':
        query += ' AND marks >= 60 AND marks < 75'
        count_query += ' AND marks >= 60 AND marks < 75'

    elif grade == 'poor':
        query += ' AND marks < 45'
        count_query += ' AND marks < 45'

    # Total students
    total = conn.execute(
        count_query,
        count_params
    ).fetchone()[0]

    # Pagination
    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'

    params.extend([per_page, offset])

    students = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    # Total pages
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'filter.html',
        students=students,
        subjects=subjects,
        selected_subject=subject,
        selected_grade=grade,
        page=page,
        total_pages=total_pages
    )

#========students===========
@app.route('/students')
def students():

    if 'username' not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    search = request.args.get('search', '').strip()

    conn = get_db(MOHINI_DB)

    if search:

        total = conn.execute(
            """
            SELECT COUNT(*)
            FROM stud
            WHERE name LIKE ?
               OR Subject LIKE ?
               OR roll_no LIKE ?
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchone()[0]

        students = conn.execute(
            """
            SELECT *
            FROM stud
            WHERE name LIKE ?
               OR Subject LIKE ?
               OR roll_no LIKE ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                per_page,
                offset
            )
        ).fetchall()

    else:

        total = conn.execute(
            "SELECT COUNT(*) FROM stud"
        ).fetchone()[0]

        students = conn.execute(
            """
            SELECT *
            FROM stud
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (per_page, offset)
        ).fetchall()

    conn.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "students.html",
        students=students,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        search=search
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

# ========== MY PROFILE ==========
@app.route("/my_profile")
def my_profile():

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db(MOHINI_DB)

    student = conn.execute(
        "SELECT * FROM stud WHERE name = ?",
        (session["username"],)
    ).fetchone()

    conn.close()

    if student is None:
        flash("Student profile not found!", "warning")
        return redirect(url_for("home"))

    return render_template(
        "detail.html",
        student=student
    )

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
            session['user_id'] = user['id']  
            session['username'] = username
            session['email'] = user['email']
            session['role'] = user['role']
            # Default language
            session['language'] = session.get('language', 'english')

            flash(f'Welcome {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/set-language/<language>')
def set_language(language):

    if language not in ['english', 'marathi']:
        language = 'english'

    session['language'] = language

    return redirect(request.referrer or url_for('home'))
@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    return redirect(url_for('feedback', user=username))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():

    if request.method == 'POST':

        rating = request.form.get('rating')
        message = request.form.get('message')
        suggestion = request.form.get('suggestion')

        username = request.args.get('user') or request.form.get('name') or "Anonymous"

        # Save feedback in database
        conn = get_db(MOHINI_DB)

        conn.execute("""
            INSERT INTO feedback (name, rating, message, suggestion)
            VALUES (?, ?, ?, ?)
        """, (
            username,
            rating,
            message,
            suggestion
        ))

        conn.commit()
        conn.close()

        # Email
        email = EmailMessage()

        email['Subject'] = f"Student Feedback - {rating}/5 ⭐"
        email['From'] = os.getenv('EMAIL_ADDRESS')
        email['To'] = os.getenv('EMAIL_ADDRESS')

        email.set_content(f"""
Student Feedback Received

Student Username: {username}

Rating: {rating}/5 ⭐

Feedback:
{message}

Suggestions for Improvement:
{suggestion if suggestion else "No suggestion provided."}

Thank you.
""")

        try:

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:

                smtp.login(
                    os.getenv('EMAIL_ADDRESS'),
                    os.getenv('EMAIL_PASSWORD')
                )

                smtp.send_message(email)

            flash(
                'Feedback submitted successfully! Thank you 😊',
                'success'
            )

        except Exception as e:
            print("========== EMAIL ERROR ==========")
            print(repr(e))
            print("EMAIL ADDRESS:", EMAIL_ADDRESS)
            print("PASSWORD SET:", bool(EMAIL_PASSWORD))
            print("=================================")

            flash(
                'Feedback submitted, but email could not be sent.',
                'danger'
            )
        return redirect(url_for('login'))

    # GET request → Feedback page 
    username = request.args.get('user', '')

    return render_template(
        'feedback.html',
        username=username
    )
@app.route('/admin/feedback')
def admin_feedback():
    if 'username' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))

    conn = get_db(MOHINI_DB)

    feedbacks = conn.execute("""
        SELECT id, name, rating, message, suggestion, created_at
        FROM feedback
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return render_template(
        'admin_feedback.html',
        feedbacks=feedbacks
    )

@app.route('/admin/feedback/delete/<int:id>', methods=['POST'])
def delete_feedback(id):

    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()

    db.execute(
        "DELETE FROM feedback WHERE id = ?",
        (id,)
    )

    db.commit()

    flash("Feedback deleted successfully!", "success")

    return redirect(url_for('admin_feedback'))
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

#============================day_AI route==============================   
@app.route("/students/<int:id>/tip")
def get_ai_tip(id):
    conn = get_db(MOHINI_DB)

    student = conn.execute(
        "SELECT * FROM stud WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        abort(404)

    prompt = f"""
    Give short 2-3 study tips.maximum 45 words, Simple, encouraging and student-friendly."""

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create( model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    tip = response.choices[0].message.content

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        tip = response.choices[0].message.content

    except Exception as e:
     tip = f"Error: {e}"
     print("GROQ ERROR:", e)

    return render_template("detail.html",student=student,tip=tip)


@app.route("/assistant")
def assistant():

    db = get_db(MOHINI_DB)

    chats = db.execute(
        """
        SELECT conversation_id,
               chat_title,
               MAX(created_at) AS created_at
        FROM chat_history
        WHERE user_id = ?
          AND conversation_id IS NOT NULL
          AND conversation_id != ''
        GROUP BY conversation_id
        ORDER BY created_at DESC
        """,
        (session.get("user_id", 0),)
    ).fetchall()

    # New conversation for fresh assistant page
    conversation_id = str(uuid.uuid4())
    session["conversation_id"] = conversation_id

    db.close()

    return render_template(
        "assistant.html",
        chats=chats,
        messages=[],
        current_conversation=conversation_id
    )
    #============================chatboat route==============================
@app.route('/chatbot', methods=['POST'])
def chatbot():

    print("=== CHATBOT ROUTE CALLED ===")

    message = request.form.get('message', '').strip()

    if not message:
        return jsonify({
            "reply": "⚠️ Please enter a message."
        })

    message_lower = message.lower()

    conn = get_db(MOHINI_DB)

    reply = None

    # ==========================================
    # SMART KEYWORD RESPONSES
    # ==========================================

    if "total students" in message_lower \
            or "count students" in message_lower \
            or message_lower == "students":

        count = conn.execute(
            "SELECT COUNT(*) AS c FROM stud"
        ).fetchone()["c"]

        reply = f"👨‍🎓 Total Students: {count}"


    elif "topper" in message_lower \
            or "highest marks" in message_lower:

        topper = conn.execute(
            """
            SELECT name, marks
            FROM stud
            ORDER BY marks DESC
            LIMIT 1
            """
        ).fetchone()

        if topper:
            reply = (
                f"🏆 Topper: {topper['name']} "
                f"with {topper['marks']} marks"
            )
        else:
            reply = "⚠️ No student data available."


    elif "lowest marks" in message_lower:

        lowest = conn.execute(
            "SELECT MIN(marks) AS m FROM stud"
        ).fetchone()

        reply = (
            f"📉 Lowest Marks: {lowest['m']}"
            if lowest and lowest["m"] is not None
            else "⚠️ No marks data available."
        )


    elif "average" in message_lower:

        average = conn.execute(
            "SELECT AVG(marks) AS avg FROM stud"
        ).fetchone()

        if average and average["avg"] is not None:
            reply = (
                f"📊 Average Marks: "
                f"{round(average['avg'], 2)}"
            )
        else:
            reply = "⚠️ No marks data available."


    elif "pass percentage" in message_lower \
            or "pass %" in message_lower:

        total = conn.execute(
            "SELECT COUNT(*) AS c FROM stud"
        ).fetchone()["c"]

        passed = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM stud
            WHERE marks >= 35
            """
        ).fetchone()["c"]

        if total > 0:
            percentage = round(
                (passed / total) * 100,
                2
            )
        else:
            percentage = 0

        reply = (
            f"✅ Pass Percentage: "
            f"{percentage}%"
        )


    elif "pass students" in message_lower:

        count = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM stud
            WHERE marks >= 35
            """
        ).fetchone()["c"]

        reply = (
            f"✅ Passed Students: {count}"
        )


    elif "fail students" in message_lower:

        count = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM stud
            WHERE marks < 35
            """
        ).fetchone()["c"]

        reply = (
            f"❌ Failed Students: {count}"
        )


    elif "subjects" in message_lower \
            or "best subject" in message_lower:

        if "best subject" in message_lower:

            subject = conn.execute(
                """
                SELECT Subject,
                       ROUND(AVG(marks),2) AS avg_marks
                FROM stud
                GROUP BY Subject
                ORDER BY avg_marks DESC
                LIMIT 1
                """
            ).fetchone()

            if subject:
                reply = (
                    f"📚 Best Subject: "
                    f"{subject['Subject']} "
                    f"(Average: {subject['avg_marks']})"
                )
            else:
                reply = "⚠️ No subject data available."

        else:

            subjects = conn.execute(
                """
                SELECT DISTINCT Subject
                FROM stud
                WHERE Subject IS NOT NULL
                AND Subject != ''
                ORDER BY Subject
                """
            ).fetchall()

            if subjects:

                subject_names = [
                    s["Subject"]
                    for s in subjects
                ]

                reply = (
                    "📚 Subjects:\n" +
                    "\n".join(
                        f"• {subject}"
                        for subject in subject_names
                    )
                )

            else:

                reply = "⚠️ No subjects available."


    elif "show students" in message_lower \
            or "student list" in message_lower:

        students = conn.execute(
            """
            SELECT name, marks
            FROM stud
            ORDER BY id DESC
            """
        ).fetchall()

        if students:

            reply = (
                "👨‍🎓 Students List:\n\n" +
                "\n".join(
                    f"• {s['name']} - {s['marks']} marks"
                    for s in students
                )
            )

        else:

            reply = "⚠️ No students available."


    elif "top 5" in message_lower:

        students = conn.execute(
            """
            SELECT name, marks
            FROM stud
            ORDER BY marks DESC
            LIMIT 5
            """
        ).fetchall()

        if students:

            reply = (
                "🏅 Top 5 Students:\n\n" +
                "\n".join(
                    f"{index + 1}. "
                    f"{s['name']} - "
                    f"{s['marks']} marks"
                    for index, s in enumerate(students)
                )
            )

        else:

            reply = "⚠️ No student data available."


    elif "recent" in message_lower:

        students = conn.execute(
            """
            SELECT name
            FROM stud
            ORDER BY id DESC
            LIMIT 5
            """
        ).fetchall()

        if students:

            reply = (
                "🕒 Recent Students:\n" +
                ", ".join(
                    s["name"]
                    for s in students
                )
            )

        else:

            reply = "⚠️ No recent students."


    elif message_lower in ["hello", "hi", "hey"]:

        reply = (
            "👋 Hello Student! "
            "How can I help you?"
        )


    elif "good morning" in message_lower:

        reply = (
            "🌅 Good Morning! "
            "Ready to learn?"
        )


    elif "good night" in message_lower:

        reply = (
            "🌙 Good Night! "
            "Take rest 😊"
        )


    elif "thanks" in message_lower \
            or "thank you" in message_lower:

        reply = (
            "🙏 You're welcome! "
            "Happy to help."
        )


    elif "college" in message_lower:

        reply = (
            "🏫 Government Polytechnic Hingoli "
            "is a technical institute."
        )


    elif "help" in message_lower:

        reply = (
            "🤖 You can ask me:\n\n"
            "• Total students\n"
            "• Topper student\n"
            "• Average marks\n"
            "• Best subject\n"
            "• Pass percentage\n"
            "• Subjects\n"
            "• Top 5 students"
        )


    # ==========================================
    # GROQ AI RESPONSE
    # ==========================================

    if not reply:

        try:

            completion = groq_client.chat.completions.create(

                model="llama-3.1-8b-instant",

                messages=[

                    {
                        "role": "system",

                        "content": """
You are Mohini's College Smart Portal AI Assistant.

Rules:

- If the user asks in Marathi, reply in simple Marathi + English mix.
- If the user asks in English, reply in simple English.
- Keep answers short and student-friendly.
- Help diploma students with study, coding, college and career questions.
- Use bullet points when useful.
"""
                    },

                    {
                        "role": "user",
                        "content": message
                    }

                ]

            )

            reply = (
                completion
                .choices[0]
                .message
                .content
            )


        except Exception as e:

            print(
                "=============================="
            )

            print(
                "GROQ ERROR:",
                e
            )

            print(
                "=============================="
            )

            reply = (
                "⚠️ AI service is currently unavailable."
            )


    # ==========================================
    # SAVE CHAT HISTORY
    # ==========================================

    user_id = session.get(
        "user_id",
        0
    )

    conversation_id = session.get(
        "conversation_id"
    )

    if not conversation_id:

        conversation_id = str(
            uuid.uuid4()
        )

        session["conversation_id"] = (
            conversation_id
        )


    print(
        "USER ID:",
        user_id
    )

    print(
        "CONVERSATION ID:",
        conversation_id
    )

    print(
        "MESSAGE:",
        message
    )

    print(
        "REPLY:",
        reply
    )


    # ==========================================
    # CHECK OLD CHAT
    # ==========================================

    old_chat = conn.execute(
        """
        SELECT id
        FROM chat_history
        WHERE conversation_id = ?
        LIMIT 1
        """,
        (conversation_id,)
    ).fetchone()


    # ==========================================
    # CHAT TITLE
    # ==========================================

    if old_chat:

        title = "College AI Chat"

    else:

        title = generate_chat_title(
            message
        )


    # ==========================================
    # INSERT CHAT
    # ==========================================

    conn.execute(
        """
        INSERT INTO chat_history
        (
            user_id,
            conversation_id,
            user_message,
            ai_reply,
            chat_title
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            conversation_id,
            message,
            reply,
            title
        )
    )


    conn.commit()

    conn.close()


    # ==========================================
    # RETURN RESPONSE
    # ==========================================

    return jsonify({
        "reply": reply
    })
@app.route("/chat-history")
def get_chat_history():

    db = get_db(MOHINI_DB)

    history = db.execute(
        """
        SELECT conversation_id,
               MAX(id) AS id,
               MAX(chat_title) AS chat_title,
               MAX(created_at) AS created_at
        FROM chat_history
        WHERE user_id = ?
          AND conversation_id IS NOT NULL
          AND conversation_id != ''
        GROUP BY conversation_id
        ORDER BY created_at DESC
        """,
        (session.get("user_id", 0),)
    ).fetchall()

    db.close()

    return jsonify([
        {
            "id": h["id"],
            "conversation_id": h["conversation_id"],
            "title": h["chat_title"] or "New Chat"
        }
        for h in history
    ])
def generate_chat_title(message):

    prompt = f"""
    Create a short chat title (2-4 words)
    from this user message.

    Message:
    {message}

    Only return title.
    """

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        title = response.choices[0].message.content.strip()
        return title

    except Exception:
        return "New Chat"

@app.route("/conversation/<conversation_id>")
def conversation(conversation_id):

    db = get_db(MOHINI_DB)

    # Selected conversation messages
    messages = db.execute(
        """
        SELECT user_message, ai_reply
        FROM chat_history
        WHERE conversation_id = ?
        ORDER BY id ASC
        """,
        (conversation_id,)
    ).fetchall()

    # Sidebar previous conversations
    chats = db.execute(
        """
        SELECT conversation_id,
               chat_title,
               MAX(created_at) AS created_at
        FROM chat_history
        WHERE user_id = ?
          AND conversation_id IS NOT NULL
          AND conversation_id != ''
        GROUP BY conversation_id
        ORDER BY created_at DESC
        """,
        (session.get("user_id", 0),)
    ).fetchall()

    db.close()

    # Continue selected conversation
    session["conversation_id"] = conversation_id

    return render_template(
        "assistant.html",
        chats=chats,
        messages=messages,
        current_conversation=conversation_id
    )
#===============ID-Card=====================
@app.route('/id_card/<int:student_id>')
def id_card(student_id):

    db = get_db(MOHINI_DB)

    student = db.execute(
        "SELECT * FROM stud WHERE id=?",
        (student_id,)
    ).fetchone()

    return render_template( 'id-card.html', student=student )


@app.route('/upload_photo/<int:id>', methods=['POST'])
def upload_photo(id):

    photo = request.files.get('photo')

    if photo and photo.filename:

        filename = secure_filename(photo.filename)

        photo.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

        db = get_db(MOHINI_DB)

        db.execute(
            "UPDATE stud SET photo=? WHERE id=?",
            (filename, id)
        )

        db.commit()

    return redirect(url_for('id_card',
                            student_id=id))

@app.route("/live_search")
def live_search():

    search = request.args.get("search", "").strip()

    conn = get_db(MOHINI_DB)

    students = conn.execute("""
        SELECT *
        FROM stud
        WHERE name LIKE ?
        OR Subject LIKE ?
        OR roll_no LIKE ?
        ORDER BY id DESC
    """,
    (
        f"%{search}%",
        f"%{search}%",
        f"%{search}%"
    )).fetchall()

    conn.close()

    result = []

    for s in students:

        if s["marks"] >= 90:
            grade = "A+"
        elif s["marks"] >= 80:
            grade = "A"
        elif s["marks"] >= 70:
            grade = "B+"
        elif s["marks"] >= 60:
            grade = "B"
        elif s["marks"] >= 50:
            grade = "C"
        else:
            grade = "Fail"

        result.append({

            "id": s["id"],
            "name": s["name"],
            "roll_no": s["roll_no"],
            "Subject": s["Subject"],
            "marks": s["marks"],
            "grade": grade,
            "photo": s["photo"] if s["photo"] else "default.png"

        })

    return jsonify(result)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
init_db()
if __name__ == "__main__":
    
    app.run(debug=True)