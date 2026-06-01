student=["Mohini","Rohini","purva","priya"]
print(student)
print(student[0])
print(student[1])
print(student[2])
print(student[3])


#loop


marks_list=[85,87,89,90]
for marks in marks_list:
    
    if marks>=90:
        print("A grade",marks_list)
    elif marks>=80:
        print("B grade",marks_list)
    elif marks>=70:
        print("C grade",marks_list)
    else:
        print("D grade",marks_list)