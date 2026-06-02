from flask import Flask
app = Flask(__name__)

stud = [
    {"name":"Rohit","roll_no":1,"marks":85},
    {"name":"Priya","roll_no":2,"marks":90},
    {"name":"Amit","roll_no":3,"marks":78},
    {"name":"Sneha","roll_no":4,"marks":92},
    {"name":"Rahul","roll_no":5,"marks":88}
  ]

@app.route('/')

def home():
  html = '<h1>Welcome to the College Smart Portal!</h1>'

  html += '<h2>List of Students:</h2>'
  for student in stud:
     html +=f"<li>{student['name']} (Roll No: {student['roll_no']}, Marks: {student['marks']})</li>"
  html +='</ul>'

  return html

@app.route('/college_info')

def college_info():
        return '<h1>College Information</h1>'

@app.route('/students')

def students():
    return '<h1>List of Students</h1>'

if __name__ == '__main__':
   app.run(debug=True)

