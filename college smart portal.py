students = ["Mohini", "Rohini", "Purva"]
marks = [90, 89, 78]
attendance = [92, 88, 95]
notices = [
    "Python internship started from 28th May 2026.",
    "We understood python internship day 3",
    "Mini Project using Python must be submitted before 9:30 PM on 30 May 2026.",
    "NextPython internship practice session is scheduled on monday."]



def student_login():
    name = input("Enter Student Name: ")
    for i in range(len(students)):

     if students[i]==name:

        print("\nLogin Successful")
        
        print("\n--- Student Details ---")
        print("Name:", name)
        print("Marks:", marks[i])
        print("Attendance:", attendance[i], "%")

        print("\n--- Notice Board ---")
        for notice in notices:
            print("#", notice)

     return

    else:
        print("Student Not Found")

student_login()
