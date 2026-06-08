from flask import Flask, render_template,request,flash,url_for,redirect
from database import get_db , init_db

app = Flask(__name__)
app.secret_key='abc1234567890'  # Needed for flashing messages


stud=[
    {"name":"Rohit  ","roll_no":1,"marks":85},
    {"name":"Priya  ","roll_no":2,"marks":90},
    {"name":"Amit   ","roll_no":3,"marks":78},
    {"name":"Sneha  ","roll_no":4,"marks":92},
    {"name":"Rahul  ","roll_no":5,"marks":88}
  ]
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
    return render_template('college_info.html', students=stud)

'''@app.route('/students')

def students():
    return render_template('students.html', students=stud)'''

@app.route('/students')
def students():
    conn = get_db()
    students = conn.execute("SELECT * FROM stud").fetchall()
    conn.close()

    return render_template('students.html', students=stud)

@app.route('/notices')

def notices():
    return render_template('notices.html', notices=notices_list)

@app.route('/about')

def about():
    return render_template('about.html')

@app.route('/add_students', methods=['GET','POST'])
def add_student():
     if request.method == "POST":
      name = request.form['student_name']
      roll_no = request.form['student_id']
      marks = int(request.form['student_marks'])
      print("student added ")  
                
      new_stud={
                "name":name,
                "roll_no":int(roll_no),
                "marks": int(marks),
               
                }

      stud.append(new_stud)
      flash(f"student added successfully" , "success") 
      print(f"new student list: {stud}")

      conn = get_db()
      conn.execute(
      "INSERT INTO stud(name, roll_no, marks) VALUES (?, ?, ?)",
      (name, roll_no, marks))
      conn.commit()
      conn.close()

     
      return redirect(url_for('add_student'))
     return render_template('add_students.html')

if __name__ == '__main__':
  init_db()
  print("Welcome to College Smart Portal")
  app.run(debug=True)

