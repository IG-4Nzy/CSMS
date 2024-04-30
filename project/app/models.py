from django.db import models
from django.contrib.auth.models import User

class Departments(models.Model):
    department_name = models.CharField(max_length = 500,null = True)
    Max_Faculty = models.IntegerField(null = True)
    def __str__(self):
        return self.department_name

class Semesters(models.Model):
    semester = models.IntegerField(null = True)

class Subject(models.Model):
    name = models.CharField(max_length=100)
    sem = models.ForeignKey(Semesters, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Principal(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null = True)
    principal_Dob = models.CharField(max_length = 100,null = True)
    principal_Doj = models.CharField(max_length = 100,null = True)
    principal_PhoneNUm = models.IntegerField(null = True)
    principal_Profile = models.FileField( upload_to = 'principal_Img',null = True)
    Is_Active = models.CharField(max_length = 10 , default="True")

class Hod(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null = True)
    Hod_Dob = models.CharField(max_length = 100,null = True)
    Hod_Doj = models.CharField(max_length = 100,null = True)
    Hod_Department = models.ForeignKey(Departments,on_delete=models.CASCADE,null = True)
    Hod_Designation = models.CharField(max_length = 100,null = True)
    Hod_PhoneNUm = models.IntegerField(null = True)
    Hod_Profile = models.FileField( upload_to = 'hod_Img',null = True)
    Is_Active = models.CharField(max_length = 10 , default="True")

    def __str__(self):
        return self.user.username
    
class HodLeaveLetter(models.Model):
    leave_Hod = models.ForeignKey(Hod,on_delete=models.CASCADE,null = True)
    leave_Principal = models.ForeignKey(Principal,on_delete=models.CASCADE,null = True)
    reason = models.CharField(max_length = 500,null = True)
    date = models.CharField(max_length = 100,null = True)
    isApproved = models.CharField(max_length = 100,null = True ,default = "False")

class Faculty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Faculty_Dob = models.CharField(max_length=100, null=True)
    Faculty_Doj = models.CharField(max_length=100, null=True)
    Faculty_Department = models.ForeignKey(Departments,on_delete=models.CASCADE,null = True)
    Faculty_Designation = models.CharField(max_length=100, null=True)
    Faculty_PhoneNUm = models.IntegerField(null=True)
    Faculty_Profile = models.FileField(upload_to='faculty_Img', null=True)
    Is_Active = models.CharField(max_length=10, default="True")
    role = models.CharField(max_length=100, null=True)
    sem = models.CharField(max_length=100, null=True)
    subjects = models.ManyToManyField('Subject', related_name='faculties')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class FacultyNotes(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    Faculty_Notes = models.FileField( upload_to = 'faculty_notes',null = True)
    Semester = models.ForeignKey(Semesters, on_delete=models.CASCADE, null=True)
    subject = models.CharField(max_length=100, null=True)
    module = models.CharField(max_length=100, null=True)

class FacultyAttendance(models.Model):
    attendance_hod = models.ForeignKey(Hod,on_delete=models.CASCADE,null = True)
    attendance_faculty = models.ForeignKey(Faculty,on_delete=models.CASCADE,null = True)
    date = models.DateField(null = True)
    month =  models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=10,null = True)
    count = models.IntegerField(null = True)

class FacultySubject(models.Model):
    faculty = models.ForeignKey(Faculty,on_delete=models.CASCADE,null = True)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE,null = True)
    sem = models.ForeignKey(Semesters, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.subject

class FacultyAssignment(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    assignment_no = models.IntegerField(null=True)
    date_of_submission = models.DateField(null=True)
    subject = models.ForeignKey(FacultySubject, on_delete=models.CASCADE, null=True)
    assignment_question = models.CharField(max_length=100, null=True)
    Sem = models.ForeignKey(Semesters, on_delete=models.CASCADE, null=True)


class Student(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    Student_Dob = models.CharField(max_length = 100,null = True)
    AdmissionNo = models.CharField(max_length = 100,null = True)
    Student_yoj = models.CharField(max_length = 100,null = True)
    Student_Department = models.ForeignKey(Departments,on_delete=models.CASCADE,null=True)
    Student_Designation = models.CharField(max_length = 100,null = True)
    Student_PhoneNum = models.IntegerField(null = True)
    roll_no = models.IntegerField(null = True)
    Student_Profile = models.FileField( upload_to = 'hod_Img',null = True)
    Is_Active = models.CharField(max_length = 10 , default="Waiting",null = True)
    Sem = models.ForeignKey(Semesters,on_delete=models.CASCADE,null=True)
    percentage = models.IntegerField(null = True)
    attendance_status = models.CharField(max_length = 100 , default="Waiting",null = True)
    attendance_statusAfternoon = models.CharField(max_length = 100 , default="Waiting",null = True)

class StudentAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    month =  models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=10)
    attendance_statusAfternoon = models.CharField(max_length = 100 , default="Waiting",null = True)
    count = models.IntegerField(null = True)

class Acadamics(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True)
    totalWorkingDays = models.IntegerField(null = True)
    department = models.CharField(max_length = 100,null = True)

class InternalMarks(models.Model):
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE,null = True)
    marks_faculty = models.ForeignKey(Faculty,on_delete=models.CASCADE,null = True)
    marks_std = models.ForeignKey(Student,on_delete=models.CASCADE,null = True)
    ass1 = models.IntegerField(null = True)
    ass2 = models.IntegerField(null = True)
    ass3 = models.IntegerField(null = True)
    tp1 = models.IntegerField(null = True)
    tp2 = models.IntegerField(null = True)
    tp3 = models.IntegerField(null = True)
    total = models.IntegerField(null = True)
    percentage = models.IntegerField(null = True)
    attendance_mark = models.IntegerField(null = True)

class StudentAssignment(models.Model):
    assignment = models.ForeignKey(FacultyAssignment, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_assignments')
    date_submitted = models.DateField(null=True)
    answer = models.FileField(upload_to='hod_Img', null=True)
    status = models.CharField(max_length = 100 , default="pending",null = True)

class Activities(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    Activity_Date = models.CharField(max_length = 100,null = True)
    Activity_Name = models.CharField(max_length = 100,null = True)
    Activity_Description = models.CharField(max_length = 100,null = True)
    Activity_images = models.FileField( upload_to = 'activity_Img',null = True)
    Is_Active = models.CharField(max_length = 10 , default="Waiting",null = True)


class Parent(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    stdParent = models.ForeignKey(Student,on_delete=models.CASCADE)
    Parent_Name = models.CharField(max_length = 100,null = True)
    Parent_num = models.CharField(max_length = 100,null = True)
    Parent_Profile = models.FileField( upload_to = 'hod_Img',null = True)
    Is_Active = models.CharField(max_length = 10 , default="Waiting",null = True)
    AdmissionNo = models.CharField(max_length = 100,null = True)

class StudentLeaveLetter(models.Model):
    leave_Student = models.ForeignKey(Student,on_delete=models.CASCADE,null = True)
    leave_Parent = models.ForeignKey(Parent,on_delete=models.CASCADE,null = True)
    leave_faculty = models.ForeignKey(Faculty,on_delete=models.CASCADE,null = True)
    reason = models.CharField(max_length = 500,null = True)
    nod = models.IntegerField(null = True)
    date = models.CharField(max_length = 100,null = True)
    isApproved = models.CharField(max_length = 100,null = True ,default = "False")
    isApprovedFaculty = models.CharField(max_length = 100,null = True ,default = "False")
    isApprovedParent = models.CharField(max_length = 100,null = True ,default = "False")

class FacultyLeaveLetter(models.Model):
    leave_Hod = models.ForeignKey(Hod,on_delete=models.CASCADE,null = True)
    leave_faculty = models.ForeignKey(Faculty,on_delete=models.CASCADE,null = True)
    reason = models.CharField(max_length = 500,null = True)
    date = models.CharField(max_length = 100,null = True)
    isApproved = models.CharField(max_length = 100,null = True ,default = "False")





    





    

    