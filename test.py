students = [
    {
        "id":1010,
        "name":"Mohini",
        "marks":90,
        "attendance":92,
        "branch":"computer Engineering",
        "years_of_study":3
    },
    {
        "id":1011,
        "name":"Rohini",
        "marks":89,
        "attendance":88,
        "branch":"computer Engineering",
        "years_of_study":2
    },
    {
        "id":1012,
        "name":"Purva",
        "marks":98,
        "attendance":95,
        "branch":"computer Engineering",
        "years_of_study":1
    },
    {
        "id":1013,
        "name":"Priya",
        "marks":85,
        "attendance":90,
        "branch":"computer Engineering",
        "years_of_study":3
    },
    {
        "id":1014,
        "name":"Pooja",
        "marks":80,
        "attendance":85,
        "branch":"computer Engineering",
        "years_of_study":2
    }
]



College_info= [
    {
        "college_name":"Goverment Polytechnic Hingoli",
        "location":"Hingoli",
        "established_year":2009,
        "available_courses":["Computer Engineering","Mechanical Engineering","Electrical & Electronics Engineering"],
        "Principal_name":"B.P.Devsarakar",

    }
]

for student in students:
    print("Student ID:", student["id"])
    print("Name:", student["name"])
    print("Marks:", student["marks"])
    print("Attendance:", student["attendance"], "%")
    print("Branch:", student["branch"])
    print("Years of Study:", student["years_of_study"])
    print("\n")


for college in College_info:
    print("College Name:", college["college_name"])
    print("Location:", college["location"])
    print("Established Year:", college["established_year"])
    print("Available Courses:", ", ".join(college["available_courses"]))
    print("Principal Name:", college["Principal_name"])

def student_login():
    name = input("Enter Student Name: ")
    for student in students:
        if student["name"] == name:
            print("\nLogin Successful")
            print("\n--- Student Details ---")
            print("Name:", student["name"])
            print("Marks:", student["marks"])
            print("Attendance:", student["attendance"], "%")
            print("Branch:", student["branch"])
            print("Years of Study:", student["years_of_study"])
            return
    print("Student Not Found")


student_login()








@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db(MOHINI_DB)
    
    if request.method == 'POST':
        name = request.form['student_name']
        marks = request.form['marks']
        subject = request.form.get('subject', '')
        attendance = request.form.get('attendance', 0)
        
        if not name:
            flash('Name cannot be empty', 'danger')
            return redirect(url_for('edit_student', id=id))
        
        conn.execute
        ('''UPDATE students SET name=?, marks=?, subject=?, attendance=? 
                     WHERE id=?''', (name, int(marks), subject, int(attendance), id))
        conn.commit()
        conn.close()
        flash(f'{name} updated successfully!', 'success')
        return redirect(url_for('students_page'))
    
