students=[
    {
    "name":"Mohini",
    "marks":90,
    "attendance":92,
    "branch":"computer Engineering",
    "years_of_study":3
    },
 {
    "name":"Rohini",
    "marks":89,
    "attendance":88,
    "branch":"computer Engineering",
    "years_of_study":2
    },
    {
    "name":"Purva",
    "marks":98,
    "attendance":95,
    "branch":"computer Engineering",
    "years_of_study":1

    },
    {
    "name":"Priya",
    "marks":85,
    "attendance":90,
    "branch":"computer Engineering",
    "years_of_study":3

    },
    {
    "name":"Pooja",
    "marks":80,
    "attendance":85,
    "branch":"computer Engineering",
    "years_of_study":2

    }
]

college_info= [
    {
        "college_name":"Goverment Polytechnic Hingoli",
        "location":"Hingoli",
        "established_year":2009,
        "available_courses":["Computer Engineering","Mechanical Engineering","Electrical & Electronics Engineering"],
        "Principal_name":"B.P.Devsarakar",

    }
]

def get_student_info(marks):
    if marks >= 90:
        return "excellent!"
    else:
        return "good but needs improvement!"

def search_student():
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
            print("Status:", get_student_info(student["marks"]))

            return 
    print("Student Not Found")
search_student()
