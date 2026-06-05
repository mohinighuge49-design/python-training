from flask import Flask, render_template
app = Flask(__name__)

stud = [
    {"name":"Rohit  ","roll_no":1,"marks":85},
    {"name":"Priya  ","roll_no":2,"marks":90},
    {"name":"Amit   ","roll_no":3,"marks":78},
    {"name":"Sneha  ","roll_no":4,"marks":92},
    {"name":"Rahul  ","roll_no":5,"marks":88}
  ]
notices_list= [
    {

        "title": "🚀python training",
        "date":    " 3 june 2026",
        "message": "💻 All students are informed that the Python Internship Program has started from 28th May 2026. ",
        "note":"The training focuses on Python programming fundamentals, problem-solving techniques,and real-world project development. ",
       "msg":"Students are encouraged to attend all sessions regularly and actively participate in practical activities to enhance their programming skills and career opportunities."
    }
    
]

@app.route('/')

def home():
    
    return render_template('home.html')

@app.route('/college_info')

def college_info():
    return render_template('college_info.html', students=stud)

@app.route('/students')

def students():
    return render_template('students.html', students=stud)

@app.route('/notices')

def notices():
    return render_template('notices.html', notices=notices_list)

if __name__ == '__main__':
  
   print("Welcome to College Smart Portal")
   app.run(debug=True)

