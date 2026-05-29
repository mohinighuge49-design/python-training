sub1=int(input("Enter marks of subject 1: "))
sub2=int(input("Enter marks of subject 2: "))
sub3=int(input("Enter marks of subject 3: "))
sub4=int(input("Enter marks of subject 4: "))
sub5=int(input("Enter marks of subject 5: "))

total=sub1+sub2+sub3+sub4+sub5
print("Total marks :", total)
percentage=(total/500)*100
print("Percentage is:", percentage)
if percentage>=75:
    print("Distinction")

elif percentage>=60: 
    print("First Class")
elif percentage>=45:
    print("pass")  
else:
    print("Fail")