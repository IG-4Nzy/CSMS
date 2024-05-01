from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User,auth
from .models import *
from datetime import date,datetime
from django.utils import timezone
from django.contrib.auth import logout
from django.http import HttpResponse,HttpResponseServerError
import calendar
from django.urls import reverse
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib import messages
from django.db.models import Subquery, OuterRef
from django.db.models import Case, When, Value, CharField
from django.db import transaction
import re
from django.http import HttpResponseRedirect
from django.http import JsonResponse




def set_password_for_all_users(new_password):
    users = User.objects.all()
    for user in users:
        user.set_password(new_password)
        user.save()
def home(request):
    # set_password_for_all_users("Pass@word1")
    # add_bulk_students()
    return render(request,'home/index.html')
def logout_view(request):
    logout(request)
    return redirect('login') 
def userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if user.is_superuser:
                auth.login(request, user)
                return redirect('adminpage')
            elif Principal.objects.filter(user=user, Is_Active="True").exists():
                auth.login(request, user)
                return redirect('PrincipalDash')
            elif Hod.objects.filter(user=user, Is_Active="True").exists():
                auth.login(request, user)
                return redirect('HodDash')
            elif Faculty.objects.filter(user=user, Is_Active="True").exists():
                auth.login(request, user)
                return redirect('FacultyDash')
            elif Student.objects.filter(user=user, Is_Active="True").exists():
                auth.login(request, user)
                return redirect('studentDash')
            elif Parent.objects.filter(user=user, Is_Active="True").exists():
                auth.login(request, user)
                return redirect('ParentDash')
            else:
                context = {'msg': 'User has no recognized role'}
                return render(request, "register/login.html", context)
        else:
         
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                context = {'msg': 'username is incorrect'}
                return render(request, "register/login.html", context)
            else:
                context = {'msg': 'Password is incorrect'}
                return render(request, "register/login.html", context)
    return render(request, 'register/login.html')
def about(request):
    return render(request,'home/about.html')
def contact(request):
    return render(request,'home/contact.html')
def services(request):
    return render(request,'home/services.html')
def testimonials(request):
    return render(request,'home/testimonials.html')


# Admin
def AddPrincipal(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('cpassword')
        email = request.POST.get('email')
        principal_Dob = request.POST.get('principalDOB')
        principal_PhoneNUm = request.POST.get('principal_PhoneNUm')
        principal_Profile = request.FILES.get('principal_Profile')

        if password != password2:
            context = {'msg': 'Passwords do not match'}
            return render(request, 'admin/AddPrincipal.html', context)
        
        if not re.match(r'^(?=.*\d)(?=.*[!@#$%^&*()-_=+{};:,<.>])(?=.*[a-zA-Z])\S{8,}$', password):
            context = {'msg': 'Password must contain at least one special character, one number, and be at least 8 characters long'}
            return render(request, 'admin/AddPrincipal.html', context)
        
        if User.objects.filter(username=username).exists():
            context = {'msg': 'Username already exists'}
            return render(request, 'admin/AddPrincipal.html', context)
        
        if Principal.objects.filter(Is_Active=True).exists():
            context = {'msg': 'Principal already exists'}
            return render(request, 'admin/AddPrincipal.html', context)
        try:
            dob = date.fromisoformat(principal_Dob)
            age = date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day))
            if age < 18:
                context = {'msg': 'You must be at least 18 years old to register'}
                return render(request, 'admin/AddPrincipal.html', context)
        except ValueError:
            pass  
        
        if not principal_PhoneNUm.isdigit() or len(principal_PhoneNUm) != 10:
            context = {'msg': 'Invalid phone number. Please enter 10 digits without spaces or special characters'}
            return render(request, 'admin/AddPrincipal.html', context)
        
        principal_Doj = date.today()
        user = User.objects.create_user(username=username, password=password, email=email)
        principal = Principal.objects.create(user=user, principal_Dob=principal_Dob, principal_Doj=principal_Doj,
                                             principal_PhoneNUm=principal_PhoneNUm, principal_Profile=principal_Profile)
        return redirect(adminpage)
    
    return render(request, 'admin/AddPrincipal.html')
def adminpage(request):
    principals = Principal.objects.filter(Is_Active="True")
    context = {
        'principal' : principals
    }
    return render(request,'admin/admin.html',context) 
def AdminDeleteSem(request,id):
    semesters = Semesters.objects.get(pk=id)
    semesters.delete()
    return redirect(ViewSemesters) 
def AdminDeleteDepartments(request,id):
    departments = Departments.objects.get(pk=id)
    departments.delete()
    return redirect(ViewDepartments)
def AdminAddDepartments(request):
    if request.method == 'POST':
        department_name = request.POST.get('department')
        if department_name:
            department = Departments.objects.create(department_name=department_name)
            department.save()
            return redirect('ViewDepartments') 
    return render(request, 'admin/AdminAddDepartments.html')
def ViewDepartments(request):
    departments = Departments.objects.all()  
    return render(request, 'admin/AdminViewDepartments.html', {'departments': departments})
def ViewSemesters(request):
    semesters = Semesters.objects.all()
    return render(request, 'admin/AdminViewSemesters.html', {'semesters': semesters})
def AdminAddSemesters(request):
    if request.method == 'POST':
        semester_name = request.POST.get('semester')
        if semester_name:
            semester = Semesters.objects.create(semester=semester_name)
            semester.save()
            return redirect('ViewSemesters')  # Assuming 'view_semesters' is the URL name for viewing semesters
    return render(request, 'admin/AdminViewSemesters.html')
def AdminAddHOD(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')  
        username = request.POST.get('username')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        doj = request.POST.get('doj')
        designation = request.POST.get('designation')
        department = request.POST.get('department')
        pnum = request.POST.get('pnum')
        password = request.POST.get('pass')
        confirm_password = request.POST.get('pass2')
        profile_picture = request.FILES.get('profile')
    
        if password != confirm_password:
            msg = 'password doesnt match'
            return render(request, 'admin/AdminAddHod.html',msg)
    
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            msg = {
                'msg':'username or email already exists',
            }
            return render(request, 'admin/AdminAddHod.html',msg)

        if Hod.objects.filter(Hod_Department = department,Is_Active = True).exists():
            msg = 'Hod Already Exists'
            return render(request, 'admin/AdminAddHod.html',msg)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        
        hod = Hod(
            user=user, 
            Hod_Dob=dob, 
            Hod_Doj=doj,
            Hod_Department=department,
            Hod_Designation=designation,
            Hod_PhoneNUm=pnum,
            Hod_Profile=profile_picture
        )
        hod.save()
    
        return redirect("adminpage")

    else:
        return render(request, 'admin/AdminAddHod.html')
def AdminViewStudents(request):
    try:
        departments = Departments.objects.all()
        selected_department_id = request.GET.get('department')
        if selected_department_id:
            department = Departments.objects.get(pk=selected_department_id)
        
        if selected_department_id:
            students = Student.objects.filter(Student_Department=department, Is_Active=True)
        else:
            students = Student.objects.filter(Is_Active=True)
        context = {
            'students': students,
            'departments': departments,
            'selected_department_id': selected_department_id,
        }
        return render(request, 'admin/AdminViewStudents.html', context)
    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {e}")
def AdminViewFaculties(request):
    try:
        faculties = Faculty.objects.filter(Is_Active=True)
        departments = Departments.objects.all()
        selected_department = request.GET.get('department')
        if selected_department:
            faculties = faculties.filter(Faculty_Department=selected_department)
        context = {
            'faculties': faculties,
            'departments': departments,
            'selected_department': selected_department,
        }
        return render(request, 'admin/AdminViewFaculty.html', context)
    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {e}")
def AdminViewHODs(request):
    admin_user = User.objects.get(username=request.user.username)
    hod = Hod.objects.filter(Is_Active="True")
    return render(request, 'admin/AdminViewHODs.html', {'admin': admin_user, 'hod': hod})
def AdminAttendance(request):
    return render(request, 'admin/attendance.html')
def AdminViewLeaveLetters(request):
    return render(request, 'admin/view_leave_letters.html')
def AdminAddFaculty(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        designation = request.POST.get('designation')
        department = request.POST.get('department')
        pnum = request.POST.get('pnum')
        password = request.POST.get('pass')
        confirm_password = request.POST.get('pass2')
        profile_picture = request.FILES.get('profile')
        
       
        if password != confirm_password:
            return HttpResponse("Passwords do not match")
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return HttpResponse("Username or email already exists")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        doj = datetime.now().strftime('%Y-%m-%d')
        faculty = Faculty.objects.create(
            user=user, 
            Faculty_Dob=dob, 
            Faculty_Doj=doj,  
            Faculty_Department=department,
            Faculty_Designation=designation,
            Faculty_PhoneNUm=pnum,
            Faculty_Profile=profile_picture
        )
        return redirect("adminpage")

    else:
        return render(request, 'admin/AdminAddFaculty.html')




# Principal
def removePrincipal(request, pk):
    # principal = get_object_or_404(Principal, id=pk)
    principal = User.objects.get(id=pk)
    principal.delete()
    return redirect(adminpage)
def PrincipalRemoveHod(request, id):
    hod = get_object_or_404(Hod, pk=id)
    hod.Is_Active = "False"
    hod.save()
    hod = Hod.objects.filter(Is_Active="True")
    context = {
        'hod': hod
    }
    return redirect("PrincipalViewHod")
def PrincipalViewHod(request):
    principal = Principal.objects.get(user = request.user)
    hod = Hod.objects.filter(Is_Active="True")  
    context = {
        'hod': hod,
        'principal': principal,
    }
    return render(request,'Principal/PrincipalViewHod.html',context)
def PrincipalViewStudents(request):
    principal = Principal.objects.get(user = request.user)
    try:
        students = Student.objects.filter(Is_Active="True")
        departments = Departments.objects.all()
        selected_department = request.GET.get('department')
        context = {
            'student': students,
            'departments': departments,
            'selected_department': selected_department,
            'principal': principal,
        }
        return render(request, 'Principal/PrincipalStudents.html', context)
    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {e}")
def PrincipalViewFaculty(request):
    principal = Principal.objects.get(user=request.user)
    try:
        faculty = Faculty.objects.filter(Is_Active=True)
        departments = Departments.objects.all()
        selected_department_id = request.GET.get('department')
        print(selected_department_id)
        
        if selected_department_id:
            # Check if the selected department ID is a valid integer
            try:
                selected_department_id = int(selected_department_id)
            except ValueError:
                selected_department_id = None

            if selected_department_id:
                # Display faculties of the selected department
                faculty = faculty.filter(Faculty_Department=selected_department_id)
                selected_department = Departments.objects.get(pk=selected_department_id)
            else:
                selected_department = None
        else:
            faculty = Faculty.objects.all()
            selected_department = None

        context = {
            'facultys': faculty,
            'departments': departments,
            'selected_department': selected_department,
            'principal': principal,
        }
        return render(request, 'Principal/PrincipalViewFaculty.html', context)
    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {e}")
def PrincipalDash(request):
    principal = Principal.objects.get(user = request.user)
    students = Student.objects.all()
    faculty = Faculty.objects.all()
    total_students = students.count()
    total_faculty = faculty.count()
    context = {
        'principal': principal,
        'student': total_students,
        'faculty': total_faculty
    }
    return render(request,'Principal/PrincipalDash.html',context)
def PrincipalAddHod(request):
    departments = Departments.objects.all()
    context = {'departments': departments}

    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('Lastname')
        username = request.POST.get('username')
        password = request.POST.get('pass')
        password2 = request.POST.get('pass2')
        email = request.POST.get('email')
        Hod_Dob = request.POST.get('dob')
        # Hod_Doj = request.POST.get('doj')
        Hod_Designation = request.POST.get('Designation')
        Hod_Department = request.POST.get('Department')
        Hod_PhoneNUm = request.POST.get('pnum')
        Hod_Profile = request.FILES.get('profile')

        submittedData = {
            'firstname':firstname,
            'lastname':lastname,
            'username':username,
            'password':password,
            'password2':password2,
            'email':email,
            'Hod_Dob':Hod_Dob,
            # 'Hod_Doj':Hod_Doj,
            'Hod_Designation':Hod_Designation,
            'Hod_Department':Hod_Department,
            'Hod_PhoneNUm':Hod_PhoneNUm,
            'Hod_Profile':Hod_Profile,
        }

        # Validate password for special character and number
        if not re.match(r'^(?=.*\d)(?=.*[!@#$%^&*()-_=+{};:,<.>])(?=.*[a-zA-Z])\S{8,}$', password):
            context['msg'] = 'Password must contain at least one special character, one number, and be at least 8 characters long'
            return render(request, 'Principal/principalAddUser.html', context)

        # Validate date of birth for 18+
        try:
            dob = date.fromisoformat(Hod_Dob)
            age = date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day))
            if age < 18:
                context['msg'] = 'You must be at least 18 years old to register'
                return render(request, 'Principal/principalAddUser.html', context)
        except ValueError:
            context['msg'] = 'Invalid Date of Birth format. Please use YYYY-MM-DD format'
            return render(request, 'Principal/principalAddUser.html', context)

        # Validate phone number for 10 digits
        if not Hod_PhoneNUm.isdigit() or len(Hod_PhoneNUm) != 10:
            context['msg'] = 'Invalid phone number. Please enter 10 digits without spaces or special characters'
            return render(request, 'Principal/principalAddUser.html', context)

        # Validate email
        # if User.objects.filter(email=email).exists():
        #     context['msg'] = 'Email already exists'
        #     return render(request, 'Principal/principalAddUser.html', context)

        # Check if passwords match
        if password != password2:
            context['msg'] = 'Passwords do not match'
            return render(request, 'Principal/principalAddUser.html', context)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            context['msg'] = 'Username already exists'
            return render(request, 'Principal/principalAddUser.html', context)

        # Check if Hod already exists in the department
        if Hod.objects.filter(Hod_Department=Hod_Department, Is_Active=True).exists():
            context['msg'] = 'Hod already exists in this department'
            return render(request, 'Principal/principalAddUser.html', context)

        # All validations pass, create Hod
        department = Departments.objects.get(pk=Hod_Department)
        user = User.objects.create_user(username=username, password=password, email=email, first_name=firstname, last_name=lastname)
        Hod.objects.create(user=user, Hod_Dob=Hod_Dob, Hod_Department=department, Hod_Designation=Hod_Designation, Hod_PhoneNUm=Hod_PhoneNUm, Hod_Profile=Hod_Profile)
        return HttpResponseRedirect(reverse('PrincipalAddHod') + '?success=1')

    return render(request, 'Principal/principalAddUser.html', context)
def PrincipalAttendance(request):
    principal = Principal.objects.get(user=request.user)
    total_students = Student.objects.filter(Is_Active="True")
    total_faculty = Faculty.objects.filter(Is_Active="True")

    if request.method == 'POST':
        selected_department = request.POST.get('selected_department')
        selected_month = request.POST.get('selected_month')
        attendance_data = FacultyAttendance.objects.filter(
            attendance_faculty__Faculty_Department=selected_department,
        )
        hod_departments = Hod.objects.values_list('Hod_Department', flat=True).distinct()
        distinct_months = FacultyAttendance.objects.filter(
            attendance_faculty__Faculty_Department=selected_department,
        ).dates('date', 'month', order='DESC')
        
        context = {
            'principal': principal,
            'student': total_students,
            'faculty': total_faculty,
            'attendance_data': attendance_data,
            'hod_departments': hod_departments,
            'distinct_months': distinct_months,
            'selected_department': selected_department,
            'selected_month': selected_month
        }
    else:
        hod_departments = Hod.objects.values_list('Hod_Department', flat=True).distinct()
        distinct_months = FacultyAttendance.objects.dates('date', 'month', order='DESC')
        current_month = datetime.now().month
        dates = FacultyAttendance.objects.filter(date__month=current_month).values_list('date', flat=True).distinct()
        attendance_data_list = []
        for department in hod_departments:
            department_attendance = {'department': department, 'attendance': []}
            for date in dates:
                attendance = FacultyAttendance.objects.filter(
                    attendance_faculty__Faculty_Department=department,
                    date=date
                ).first()
                department_attendance['attendance'].append(attendance)
            attendance_data_list.append(department_attendance)
        
        context = {
            'principal': principal,
            'student': total_students,
            'faculty': total_faculty,
            'hod_departments': hod_departments,
            'distinct_months': distinct_months,
            'attendance_data': attendance_data_list
        }

    return render(request, 'Principal/PrincipalAttendance.html', context)
def PrincipalViewLeaveletters(request):
    principal = Principal.objects.get(user=request.user)
    hod_leave_letters = HodLeaveLetter.objects.filter(isApproved=False)

    context = {
        'principal': principal,
        'hod_leave_letters': hod_leave_letters
    }
    return render(request, 'principal/PrincipalViewLeaveletters.html', context)
def approve_reject_leavePrincipal(request, leave_id):
    principal = Principal.objects.get(user=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        leave_letter = HodLeaveLetter.objects.get(id=leave_id)
        if status == "approve":
            leave_letter.isApproved = True
            leave_letter.save()
            hod = Hod.objects.filter(Hod_Department=leave_letter.leave_Hod.Hod_Department, Is_Active=False).first()
            if hod:
                principal_name = principal.user.get_full_name()
                hod_name = hod.user.get_full_name()
                current_date = timezone.now().strftime('%Y-%m-%d')

                subject = f'Leave Letter Approved by {principal_name}'
                message = f'Leave request for {hod_name} has been approved by {principal_name} on {current_date}'
                hod_email = hod.user.email

                send_mail(subject, message, 'sampleproject2211@gmail.com', [hod_email], fail_silently=False)

        elif status == "reject":
            leave_letter.isApproved = False
            leave_letter.save()
            hod = Hod.objects.filter(Hod_Department=leave_letter.leave_Hod.Hod_Department, Is_Active=False).first()
            if hod:
                principal_name = principal.user.get_full_name()
                hod_name = hod.user.get_full_name()
                current_date = timezone.now().strftime('%Y-%m-%d')

                subject = f'Leave Letter Rejected by {principal_name}'
                message = f'Leave request for {hod_name} has been rejected by {principal_name} on {current_date}'
                hod_email = hod.user.email

                send_mail(subject, message, 'sampleproject2211@gmail.com', [hod_email], fail_silently=False)

    return redirect('PrincipalViewLeaveletters')
def PrincipalEditProfile(request, user_id):
    # Get the current logged-in principal
    principal = Principal.objects.get(user=request.user)
    user = principal.user  # Get the associated user object
    
    if request.method == 'POST':
        # Update the profile fields based on the form data
        principal.principal_Dob = request.POST.get('dob')
        principal.principal_Doj = request.POST.get('doj')
        principal.principal_PhoneNUm = request.POST.get('phone_num')
        
        # Update first name and last name
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        
        # Check if a new profile picture is uploaded
        if request.FILES.get('profile_pic'):
            principal.principal_Profile = request.FILES['profile_pic']
        
        principal.save()
        
        # Redirect to a success page or back to the profile page
        return redirect('profile')
    
    # Render the edit profile form template with the current profile details
    return render(request, 'Principal/PrincipalEditProfile.html', {'principal': principal, 'user': user})


# Hod
def removeHod(request, pk):
    hod = get_object_or_404(Hod, id=pk)
    hod.Is_Active = False  # Assuming Is_Active is a boolean field
    hod.save()
    hods = Hod.objects.filter(Is_Active=True)
    context = {
        'hod': hods
    }
    user = request.user
    user = User.objects.get(username = user)
    if user.is_superuser:
        return redirect('AdminViewHODs')
    else:
        return redirect('PrincipalViewHod')
def HodDeleteSubjects(request,id):
    subjects = Subject.objects.get(pk = id)
    subjects.delete()
    return redirect(HodAddSubjects)
def HodAddSubjects(request):   
    semesters = Semesters.objects.all()
    context = {
        'semesters':semesters,
    }
    hod = Hod.objects.get(user=request.user)
    subjects = Subject.objects.filter(department=hod.Hod_Department)
    if request.method == 'POST':
        subject_name = request.POST.get('subjects')
        sem = request.POST.get('sem')
        semester = Semesters.objects.get(pk=sem)
        if subject_name:
            print(hod.Hod_Department.id)
            department = Departments.objects.get(pk=hod.Hod_Department.id)
            subject = Subject.objects.create(name=subject_name, department=department,sem=semester)
            print(subject)
            subject.save()
            return redirect('HodAddSubjects')
    context = {
        'subjects': subjects,
        'semesters':semesters,
        'hod':hod,
    }
    return render(request, 'hod/HodAddSubjects.html', context)
def HodDash(request):
    hod = Hod.objects.get(user=request.user)
    faculties = Faculty.objects.filter(Faculty_Department=hod.Hod_Department)
    total_students = Student.objects.filter(Student_Department=hod.Hod_Department).count()
    total_faculty = faculties.count()
    # all_subjects = Subject.objects.filter(faculty__in=faculties)
    Facultysubjects = FacultySubject.objects.filter(department = hod.Hod_Department)
    subjects = Subject.objects.filter(department = hod.Hod_Department)
    context = {
        'student_count': total_students,
        'faculty_count': total_faculty,
        'hod': hod,
        'faculties': faculties,
        'subjects': subjects,
        'Facultysubjects': Facultysubjects,
    }
    return render(request, 'hod/HodDash.html', context)
def update_role(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        role = request.POST.get('role')
        
        try:
            faculty = Faculty.objects.get(pk=faculty_id)
            department = faculty.Faculty_Department
            sem = faculty.sem
            
            # Check if any of the tutor roles are already assigned for the department
            existing_tutors = Faculty.objects.filter(Q(role__startswith='tutor') & Q(Faculty_Department=department) & Q(sem=sem))
            
            # Extract existing tutor roles
            existing_tutor_roles = set(f.role for f in existing_tutors)
            
            # If the selected role is a tutor role and it's already assigned for the department, display an error message
            if role in existing_tutor_roles:
                messages.error(request, f'The role "{role}" is already assigned as a tutor for this department and semester.')
                return redirect('HodDash')
            
            # Update the faculty's role
            faculty.role = role
            faculty.save()
            
        except Faculty.DoesNotExist:
            return redirect('HodDash')

        return redirect('HodDash')

    # Handle other request methods (e.g., GET) by returning an empty HttpResponse
    return HttpResponse()
def update_subjects(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        subjects = request.POST.get('subjects')
        print(subjects)
        try:
            faculty_id = int(faculty_id) 
            print(faculty_id)
        except ValueError:
            return redirect('HodDash')

        print("Subjects:", subjects)
        faculty = Faculty.objects.get(pk=faculty_id)
        print(faculty)
        if subjects:
            faculty.subjects.clear()
            subject = Subject.objects.get(pk = subjects)
            sem = Semesters.objects.get(semester = subject.sem.semester)
            department = Departments.objects.get(department_name = subject.department.department_name)
            SubjectExists = FacultySubject.objects.filter(subject = subject, faculty=faculty,sem=sem,department=department)
            if not SubjectExists:
                subjects = FacultySubject.objects.create(subject = subject, faculty=faculty,sem=sem,department=department)
                subjects.save()
            else:
                SubjectExists.delete()
                subjects = FacultySubject.objects.create(subject = subject, faculty=faculty,sem=sem,department=department)
                subjects.save()

        return redirect('HodDash')
def HodAttendance(request):
    hod = Hod.objects.get(user=request.user)
    selected_class = request.GET.get('selected_class', "0")
    start_semester = (int(selected_class) - 1) * 2 + 1
    end_semester = start_semester + 1
    attendance_data = StudentAttendance.objects.filter(
        student__Sem__in=range(start_semester, end_semester + 1),
        student__Student_Department=hod.Hod_Department
    )
    students = Student.objects.filter(Sem__in=range(start_semester, end_semester + 1),Is_Active="True")
    attendance_data_list = []
    current_month = datetime.now().month
    dates = StudentAttendance.objects.filter(month=current_month).values_list('date', flat=True).distinct()
    for student in students:
        student_attendance = {'student': student, 'attendance': []}
        for date in dates:
            attendance = attendance_data.filter(student=student, date=date).first()
            student_attendance['attendance'].append(attendance)
        attendance_data_list.append(student_attendance)
    context = {
        'attendance_data': attendance_data_list,
        'selected_class': selected_class,
        'hod': hod,
        'dates': dates, 
    }

    return render(request, 'hod/HodAttendance.html', context)
def HodStudents(request):
    try:
        hod = get_object_or_404(Hod, user=request.user)
        selected_class = request.session.get('selected_class', "1")

        if request.method == 'POST':
            selected_class = request.POST.get('selected_class', "1")
            request.session['selected_class'] = selected_class
        start_semester = (int(selected_class) - 1) * 2 + 1
        end_semester = start_semester + 1
        students = Student.objects.filter(Student_Department=hod.Hod_Department, Sem__in=range(start_semester, end_semester + 1),Is_Active="True")
        context = {
            'students': students,
            'hod': hod,
            'selected_class': selected_class,
        }
        return render(request, 'hod/HodStudents.html', context)
    
    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {e}")
def HodNotes(request):
    hod = get_object_or_404(Hod, user=request.user)
    hod_department = hod.Hod_Department 
    hod_notes = FacultyNotes.objects.filter(faculty__Faculty_Department=hod_department)

    context = {
        'hod': hod,
        'notes': hod_notes,
    }
    return render(request, 'hod/HodNotes.html', context)
def HodInternal(request):
    hod = Hod.objects.get(user=request.user)
    students = Student.objects.filter(Student_Department=hod.Hod_Department)
    selected_year = request.GET.get('selected_year')
    if selected_year:
        selected_year = int(selected_year)
        request.session['selected_year'] = selected_year
    else:
        selected_year = request.session.get('selected_year')
    if selected_year == 1:
        semesters = [1, 2] 
    elif selected_year == 2:
        semesters = [3, 4]  
    else:
        semesters = [5, 6] 
    internal_marks = InternalMarks.objects.filter(marks_std__in=students, marks_std__Sem__in=semesters)

    context = {
        'students': students,
        'internal_marks': internal_marks,
        'hod': hod,
        'selected_year': selected_year
    }
    return render(request, 'hod/HodInternal.html', context)
def HodLeave(request):
    hod = Hod.objects.get(user=request.user)
    principal = Principal.objects.get(Is_Active = "True")
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        reason = request.POST.get('reason')
        
        hod_leave_letter = HodLeaveLetter.objects.create(
            leave_Hod=hod,
            leave_Principal=principal,
            date=date,
            reason=reason
        )
        hod_leave_letter.save()

        subject = f"Leave Request from {name}"
        message = f"Dear {principal.user.first_name},\n\n{name} has requested leave on {date} for the following reason:\n\n{reason}"
        from_email = "sampleproject2211@gmail.com" 
        recipient_list = [principal.user.email]
        print(recipient_list)
        send_mail(subject, message, from_email, recipient_list)
    
    return render(request, 'hod/HodLeave.html', {'hod': hod})
def HodAddFaculty(request):
    departments = Departments.objects.all()
    context = {'departments': departments}
    hod = Hod.objects.get(user=request.user)

    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        password = request.POST.get('pass')
        password2 = request.POST.get('pass2')
        email = request.POST.get('email')
        Faculty_Dob = request.POST.get('dob')
        Faculty_Doj = request.POST.get('doj')
        Faculty_Designation = request.POST.get('designation')
        Faculty_Department = hod.Hod_Department
        Faculty_PhoneNUm = request.POST.get('pnum')
        Faculty_Profile = request.FILES.get('profile')

        # Validate password for special character and number
        if not re.match(r'^(?=.*\d)(?=.*[!@#$%^&*()-_=+{};:,<.>])(?=.*[a-zA-Z])\S{8,}$', password):
            context['msg'] = 'Password must contain at least one special character, one number, and be at least 8 characters long'
            return render(request, 'hod/HodAddUser.html', context)

        # Validate mobile number format
        if not re.match(r'^\d{10}$', Faculty_PhoneNUm):
            context['msg'] = 'Invalid mobile number format. Please enter 10 digits without spaces or special characters'
            return render(request, 'hod/HodAddUser.html', context)

        if password != password2:
            context['msg'] = 'Passwords do not match'
            return render(request, 'hod/HodAddUser.html', context)
        else:
            if Faculty.objects.filter(user__username=username).exists():
                context['msg'] = 'Username already exists'
                return render(request, 'hod/HodAddUser.html', context)
            
            if User.objects.filter(username=username).exists():
                context['msg'] = 'Username already exists'
                return render(request, 'hod/HodAddUser.html', context)

            if Faculty.objects.filter(user__email=email).exists():
                context['msg'] = 'Email already exists'
                return render(request, 'hod/HodAddUser.html', context)
            else:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=firstname, last_name=lastname)
                Faculty.objects.create(user=user, Faculty_Dob=Faculty_Dob, Faculty_Doj=Faculty_Doj, Faculty_PhoneNUm=Faculty_PhoneNUm, Faculty_Profile=Faculty_Profile, Faculty_Department=Faculty_Department, Faculty_Designation=Faculty_Designation)
                return HttpResponseRedirect(reverse('HodAddFaculty') + '?success=1')
    return render(request, 'hod/HodAddUser.html', context)
def HodViewLeaveletters(request):
    hod = Hod.objects.get(user=request.user)
    hod_leave_letters = FacultyLeaveLetter.objects.filter(leave_Hod__Hod_Department=hod.Hod_Department, isApproved=False)
    std_leave_letters = StudentLeaveLetter.objects.filter(leave_Student__Student_Department=hod.Hod_Department, isApprovedFaculty=True ,isApproved=False)
    print(hod_leave_letters)
    print(std_leave_letters)

    context = {
        'hod_leave_letters': hod_leave_letters,
        'hod':hod,
        'std_leave_letters':std_leave_letters,
    }
    return render(request, 'hod/HodViewLeaveletters.html', context)
def approve_reject_leaveHodFaculty(request, leave_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        leave_letter = FacultyLeaveLetter.objects.get(id=leave_id)
        if status == "approve":
            leave_letter.isApproved = True
            leave_letter.save()

            # Send email to faculty
            hod = Hod.objects.get(user=request.user)
            hod = leave_letter.leave_Hod
            faculty = leave_letter.leave_faculty
            current_date = datetime.now().strftime('%Y-%m-%d')

            subject = 'Leave Letter Approved for {}'.format(faculty.user.first_name)
            message = '{} has approved the leave request for {} on {}'.format(hod.user.first_name, faculty.user.first_name, current_date)
            faculty_email = faculty.user.email

            send_mail(subject, message, 'sampleproject2211@gmail.com', [faculty_email], fail_silently=False)
            leave_letter.delete()
        elif status == "reject":
            leave_letter.isApprovedFaculty = False
            leave_letter.save()

            hod = Hod.objects.get(user=request.user)
            hod = leave_letter.leave_Hod
            faculty = leave_letter.leave_faculty
            current_date = datetime.now().strftime('%Y-%m-%d')

            subject = 'Leave Letter Rejected for {}'.format(faculty.user.first_name)
            message = '{} has Rejected the leave request for {} on {}'.format(hod.user.first_name, faculty.user.first_name, current_date)
            faculty_email = faculty.user.email

            send_mail(subject, message, 'sampleproject2211@gmail.com', [faculty_email], fail_silently=False)
            leave_letter.delete()

    return redirect('HodViewLeaveletters')
def approve_reject_leaveHodStudent(request, leave_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        leave_letter = StudentLeaveLetter.objects.get(id=leave_id)
        if status == "approve":
            leave_letter.isApproved = True
            leave_letter.save()
            # Send email to Student
            hod = Hod.objects.get(user=request.user)
            student = leave_letter.leave_Student
            current_date = datetime.now().strftime('%Y-%m-%d')

            subject = 'Leave Letter Approved for {}'.format(student.user.first_name)
            message = '{} has approved the leave request for {} on {}'.format(hod.user.first_name, student.user.first_name, current_date)
            student_email = student.user.email
            send_mail(subject, message, 'sampleproject2211@gmail.com', [student_email], fail_silently=False)

        elif status == "reject":
            leave_letter.isApprovedFaculty = False
            leave_letter.isApproved = 'rejected'
            leave_letter.save()

            hod = Hod.objects.get(user=request.user)
            student = leave_letter.leave_Student
            current_date = datetime.now().strftime('%Y-%m-%d')

            subject = 'Leave Letter Rejected for {}'.format(student.user.first_name)
            message = '{} has Rejected the leave request for {} on {}'.format(hod.user.first_name, student.user.first_name, current_date)
            faculty_email = student.user.email

            send_mail(subject, message, 'sampleproject2211@gmail.com', [faculty_email], fail_silently=False)

    return redirect('HodViewLeaveletters')
def HodAddAttendance(request):
    hod = Hod.objects.get(user=request.user)
    hod_department = hod.Hod_Department
    faculties = Faculty.objects.filter(Faculty_Department=hod_department)
    
    return render(request, 'hod/HodAddAttendance.html', {'faculties': faculties , 'hod' : hod})   
def MarkAttendanceFaculty(request , pk):
    faculty = Faculty.objects.get(id=pk)
    status = request.POST.get('status')
    current_date = datetime.now()
    attendance, created = FacultyAttendance.objects.get_or_create(
        attendance_faculty=faculty,
        date=current_date,
        defaults={'status': 'Absent'},
        month=current_date.month
    )
    if not created:
        attendance.status = status
        attendance.save()
    return redirect(reverse('HodAddAttendance'))
def HodViewAttendance(request):
    hod = Hod.objects.get(user=request.user)
    hod_department = hod.Hod_Department
    attendance_data = FacultyAttendance.objects.filter(attendance_faculty__Faculty_Department=hod_department)
    context = {
        'hod':hod,
        'attendance_data' : attendance_data,
    }
    return render(request, 'hod/HodViewAttendance.html',context)
def remove_subject(request, subject_id):
    
    subject = Subject.objects.get(id=subject_id)
    subject.delete()
    return redirect('HodDash')
def deleteFaculty(request, id):
    faculty = Faculty.objects.get(id=id)
    faculty.delete()
    return redirect('HodDash')
def HodViewFaculties(request):
    try:
        faculties = Faculty.objects.filter(Is_Active=True)
        hod = Hod.objects.get(user=request.user)
        departments = Departments.objects.get(department_name = hod.Hod_Department.department_name)
        if departments:
            faculties = faculties.filter(Faculty_Department=departments)
        context = {
            'faculties': faculties,
        }
        return render(request, 'hod/HodViewFaculty.html', context)
    except Exception as e:
        return HttpResponseServerError(f"An error occurred: {e}")
    

# Faculty
def removeFaculty(request, pk):
    faculty = get_object_or_404(Faculty, id=pk)
    faculty.Is_Active = "False"
    faculty.save()
    facultys = Faculty.objects.filter(Is_Active="True")
    context = {
        'faculty': facultys
    }
    return redirect(PrincipalViewFaculty,context)  
def FacultyDash(request):
    faculty = Faculty.objects.get(user = request.user)
    students = Student.objects.filter(Student_Department=faculty.Faculty_Department, Is_Active=True)
    faculties = Faculty.objects.filter(Faculty_Department=faculty.Faculty_Department)
    total_students = students.count()
    total_faculty = faculties.count()
    context = {
        'faculty': faculty,
        'student': total_students,
        'faculties': total_faculty
    }
    return render(request,'faculty/FacultyDash.html',context)
def facultyAttendance(request):
    faculty = Faculty.objects.get(user = request.user)
    if request.method == 'POST':
        selected_class = request.POST.get('classDropdown', "1")
        request.session['selected_class'] = selected_class
    else:
        selected_class = request.session.get('selected_class', "1")

    start_semester = (int(selected_class) - 1) * 2 + 1
    end_semester = start_semester + 1
    students = Student.objects.filter(Student_Department=faculty.Faculty_Department, Sem__in=range(start_semester, end_semester + 1))
    attendance_records = StudentAttendance.objects.filter(student__in=students)

    context = {
        'students': students,
        'faculty': faculty,
        'attendance_records': attendance_records,
        'selected_class': selected_class,
    }
    return render(request, 'faculty/FacultyAttendance.html', context)
def MarkAttendance(request, pk):
    faculty = get_object_or_404(Faculty, user=request.user)
    student = get_object_or_404(Student, id=pk)
    status = request.POST.get('status')
    if status == 'present':
        attendance_status = 'present'
    else:
        attendance_status = 'absent'
    current_date = datetime.now()
    month = current_date.month
    attendance, created = StudentAttendance.objects.get_or_create(
        student=student,
        date=current_date,
        defaults={'status': 'Absent'}, 
        month=month
    )
    attendance.status = attendance_status
    student.attendance_status = attendance_status
    student.save()
    attendance.save()
    return redirect(reverse('facultyAttendance'))
def MarkAttendanceAfternoon(request, pk):
    faculty = get_object_or_404(Faculty, user=request.user)
    student = get_object_or_404(Student, id=pk)
    status = request.POST.get('status')
    if status == 'present':
        attendance_status = 'present'
    else:
        attendance_status = 'absent'
    current_date = datetime.now()
    month = current_date.month
    attendance, created = StudentAttendance.objects.get_or_create(
        student=student,
        date=current_date,
        defaults={'status': 'Absent'}, 
        month=month
    )
    attendance.attendance_statusAfternoon = attendance_status
    student.attendance_statusAfternoon = attendance_status
    student.save()
    attendance.save()
    return redirect(reverse('facultyAttendance'))
def promote_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    print(student.Sem.semester)
    if student.Sem.semester >= 6:
        return HttpResponse('Student is already in the final semester')
    Sem = student.Sem.semester
    Sem += 1
    print(Sem)
    sem = Semesters.objects.get(id=Sem)
    print(sem.semester)
    Students = Student.objects.get(pk=student.id)
    print(Students)
    Students.Sem = sem
    print(Students.Sem.semester)
    Students.save()
    return redirect('FacultyStudents')
def display_students(request):
    students = []
    selected_year = request.session.get('selected_year', timezone.now().year)
    if request.method == 'POST':
        selected_year = int(request.POST.get('selected_year', selected_year))
        request.session['selected_year'] = selected_year
        year = 1
        if selected_year == 1:
            year = 1
        elif selected_year == 2:
            year = 3
        else:
            year = 5
        students = Student.objects.filter(Sem__in=[year, year+1])
        return redirect('FacultyStudents', year=selected_year)
    return render(request, 'faculty/FacultyStudents.html', {'students': students, 'selected_year': selected_year})
def display_months(request):
    faculty = Faculty.objects.get(user=request.user)
    unique_months = StudentAttendance.objects.filter(student__Student_Department=faculty.Faculty_Department).dates('date', 'month').distinct()
    unique_months = [month.strftime('%B') for month in unique_months]
    return render(request, 'faculty/FacultyStudents.html', {'unique_months': unique_months})
def FacultyViewAttendance(request):
    faculty = Faculty.objects.get(user=request.user)
    selected_class = request.GET.get('selected_class', "0")
    start_semester = (int(selected_class) - 1) * 2 + 1
    end_semester = start_semester + 1
    attendance_data =  StudentAttendance.objects.filter(student__Sem__in=range(start_semester, end_semester + 1)
    )
    students = Student.objects.filter(Sem__in=range(start_semester, end_semester + 1))
    current_month = datetime.now().month
    dates = StudentAttendance.objects.filter(month=current_month).values_list('date', flat=True).distinct()
    attendance_data_list = []
    for student in students:
        student_attendance = {'student': student, 'attendance': []}
        for date in dates:
            attendance = attendance_data.filter(student=student, date=date).first()
            student_attendance['attendance'].append(attendance)
        attendance_data_list.append(student_attendance)
    
    context = {
        'students': students,
        'dates': dates,
        'attendance_data': attendance_data_list,
        'faculty': faculty,
        'selected_class': selected_class,
    }
    
    return render(request, 'faculty/FacultyViewAttendance.html', context)
def FacultyStudents(request):
    faculty = get_object_or_404(Faculty, user=request.user)
    selected_class = request.POST.get('selected_class', "1")
    start_semester = (int(selected_class) - 1) * 2 + 1
    end_semester = start_semester + 1
    students = Student.objects.filter(
    Q(Student_Department=faculty.Faculty_Department) &
    Q(Sem__in=range(start_semester, end_semester + 1)) &
    Q(Is_Active=True)
    )
    context = {
        'students': students,
        'faculty': faculty,
        'selected_class': selected_class,
    }
    return render(request, 'faculty/FacultyStudents.html', context)
def facultyNotes(request):
    faculty = get_object_or_404(Faculty, user=request.user)
    faculty_department = faculty.Faculty_Department 
    faculty_notes = FacultyNotes.objects.filter(faculty__Faculty_Department=faculty_department)

    context = {
        'faculty': faculty,
        'notes': faculty_notes,
    }
    return render(request, 'faculty/FacultyNotes.html', context)
def add_notes(request):
    faculty = get_object_or_404(Faculty, user=request.user)
    subjects = FacultySubject.objects.filter(faculty=faculty)
    semesters = Semesters.objects.all()

    if request.method == 'POST':
        subject = request.POST.get('subject')
        module = request.POST.get('module')
        pdf_file = request.FILES.get('pdf_file')
        semester = request.POST.get('semester')
        semester = Semesters.objects.get(semester=semester)
        FacultyNotes.objects.create(
            faculty=faculty,
            Faculty_Notes=pdf_file,
            Semester=semester,
            subject=subject,
            module=module
        )

        return redirect('FacultyNotes')

    context = {
        'faculty': faculty,
        'subjects': subjects,
        'semesters': semesters,
    }
    return render(request, 'faculty/facultyaddnotes.html', context)
def delete_note(request, note_id):
    note = get_object_or_404(FacultyNotes, id=note_id)
    note.delete()
    return redirect('FacultyNotes')
def FacultyInternal(request):
    try:
        faculty = get_object_or_404(Faculty, user=request.user)
        selected_class = request.session.get('selected_class')
        semesters = Semesters.objects.all()

        if request.method == 'POST':
            selected_class = request.POST.get('classDropdown')
            request.session['selected_class'] = selected_class

        if not selected_class:
            selected_class = '1'

        Sem = Semesters.objects.get(pk=selected_class)
   
        # Filter subjects based on the selected semester
        subjects = Subject.objects.filter(sem=Sem)
        students = Student.objects.filter(Sem=Sem)


        internal_marks = InternalMarks.objects.filter(
            marks_std__Student_Department=faculty.Faculty_Department,
            marks_std__Sem=Sem,
            subject__in=subjects
        )

        if not internal_marks:
             for student in students:
                for subject in subjects:
                    print(subject)
                    if not InternalMarks.objects.filter(marks_std=student, subject=subject).exists():
                        InternalMarks.objects.create(
                            marks_std=student,
                            subject=subject,
                            ass1=0,
                            ass2=0,
                            ass3=0,
                            tp1=0,
                            tp2=0,
                            tp3=0,
                            total=0,
                            percentage=0,
                            attendance_mark=0
                        )

        try:
            with transaction.atomic(): 
                for mark in internal_marks:
                    total_marks = 0
                    if all(getattr(mark, f) is not None for f in ['ass1', 'ass2', 'ass3', 'tp1', 'tp2', 'tp3']):
                        total_marks += (mark.ass1 + mark.ass2 + mark.ass3) 
                        total_marks += (mark.tp1 + mark.tp2 + mark.tp3)  
                    
                    # Update total marks
                    mark.percentage = total_marks
                    mark.save()

                    # Update related Student's total marks
                    mark.marks_std.percentage = total_marks
                    mark.marks_std.save()

        except Exception as e:
            # Handle exceptions
            print(e)
        context = {
            'internal_marks': internal_marks,
            'faculty': faculty,
            'selected_class': selected_class,
            'subjects': subjects,
            'students': students,
            'semesters':semesters,
        }

        return render(request, 'faculty/FacultyInternal.html', context)
    except Exception as e:
        print("Error:", e)
        return render(request, 'faculty/FacultyInternal.html', {'error_message': str(e)})
def FacultyLeave(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        reason = request.POST.get('reason')
        faculty = get_object_or_404(Faculty, user=request.user)
        hod = Hod.objects.get(Hod_Department=faculty.Faculty_Department, Is_Active=True)
        leave_letter = FacultyLeaveLetter.objects.create(
            leave_Hod=hod,
            leave_faculty=faculty,
            reason=reason,
            date=date
        )
        subject = f"Leave Request from {name}"
        message = f"Dear {hod.user.first_name},\n\n{name} has requested leave on {date} for the following reason:\n\n{reason}"
        from_email = "sampleproject2211@gmail.com"
        recipient_list = [hod.user.email]
        print(recipient_list)
        send_mail(subject, message, from_email, recipient_list)
        return redirect('FacultyLeave') 

    faculty = get_object_or_404(Faculty, user=request.user)
    context = {
        'faculty': faculty
    }
    return render(request, 'faculty/FacultyLeave.html', context)
def FacultyViewLeaveletters(request):
    faculty = Faculty.objects.get(user=request.user)  
    student_leave_letters = StudentLeaveLetter.objects.filter(leave_faculty=faculty, isApprovedParent=True , isApprovedFaculty="False")
    context = {
        'student_leave_letters': student_leave_letters,
        'faculty':faculty
    }
    return render(request, 'faculty/FacultyViewLeaveletters.html', context)
def approve_reject_leaveFaculty(request, leave_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        leave_letter = StudentLeaveLetter.objects.get(id=leave_id)
        if status == "approve":
            leave_letter.isApprovedFaculty = True
        elif status == "reject":
            leave_letter.isApprovedFaculty = 'rejected'
        leave_letter.save()

    if leave_letter.isApprovedFaculty == True:
        faculty = Faculty.objects.get(user=request.user)
        parent = Parent.objects.get(id=leave_letter.leave_Parent.id) 
        student = Student.objects.get(id=leave_letter.leave_Student.id)
        current_date = datetime.now().strftime('%Y-%m-%d')

        subject = 'Leave Letter Approved for {}'.format(student.user.first_name)
        message = '{} has approved the leave request for {} on {}'.format(faculty.user.first_name, student.user.first_name, current_date)
        student_email = student.user.email
        parent_email = parent.user.email

        send_mail(subject, message, 'sampleproject2211@gmail.com', [student_email], fail_silently=False)
        send_mail(subject, message, 'sampleproject2211@gmail.com', [parent_email], fail_silently=False)
    else:
        faculty = Faculty.objects.get(user=request.user)
        parent = Parent.objects.get(id=leave_letter.leave_Parent.id) 
        student = Student.objects.get(id=leave_letter.leave_Student.id)
        current_date = datetime.now().strftime('%Y-%m-%d')

        subject = 'Leave Letter Rejected for {}'.format(student.user.first_name)
        message = '{} has rejected the leave request for {} on {}'.format(faculty.user.first_name, student.user.first_name, current_date)
        student_email = student.user.email
        parent_email = parent.user.email

        send_mail(subject, message, 'sampleproject2211@gmail.com', [student_email], fail_silently=False)
        send_mail(subject, message, 'sampleproject2211@gmail.com', [parent_email], fail_silently=False)

        leave_letter.delete()

    return redirect('FacultyViewLeaveletters')
def StdApprove(request):
    faculty = Faculty.objects.get(user = request.user)
    if not faculty.role == "tutor1":
        return HttpResponse("You do not have permission to approve student requests.")
    
    students = Student.objects.filter(Student_Department=faculty.Faculty_Department, Is_Active="Waiting")
    context = {
        'faculty': faculty,
        'student' : students
    }
    return render(request,'faculty/StdApprove.html',context)
def ParentApprove(request):
    faculty = Faculty.objects.get(user = request.user)
    if not faculty.role == "tutor1":
        return HttpResponse("You do not have permission to approve student requests.")
    parents = Parent.objects.filter(Is_Active="Waiting")
    context = {
        'parent' : parents,
        'faculty':faculty
    }
    return render(request,'faculty/Parentapprove.html',context)
def StdApproval(request,pk):
    students = Student.objects.get(id=pk)
    students.Is_Active = "True"
    today = date.today()
    year = today.year
    length = len(str(students.id))
    print(length)
    if length < 2:
        num = '00' + str(students.id)
    else:
        num = str(students.id)
    students.AdmissionNo = str(year)+str(num)
    students.save()
    return redirect(StdApprove)
def ParentApproval(request,pk):
    parents = Parent.objects.get(id=pk)
    parents.Is_Active = "True"
    parents.save()
    return redirect(ParentApprove)    
def removeStudent(request, pk):
    student = get_object_or_404(Student, id=pk)
    student.Is_Active = "False"
    student.save()
    students = Student.objects.filter(Is_Active="True")
    context = {
        'student': students
    }
    return redirect(FacultyStudents)
def faculty_add_assignment(request):
    faculty = Faculty.objects.get(user=request.user)
    subjects = FacultySubject.objects.filter(faculty=faculty)
    semesters = Semesters.objects.all()
    context = {
        'faculty': faculty,
        'subjects': subjects,
        'semesters': semesters,
    }
    
    if request.method == 'POST':
        assignment_no = request.POST.get('assignment_no')
        date_of_submission = request.POST.get('date_of_submission')
        subject = request.POST.get('subject')
        assignment_question = request.POST.get('assignment_question')
        semester_id = request.POST.get('semester')

        # Convert date_of_submission to datetime object
        date_of_submission = datetime.strptime(date_of_submission, '%Y-%m-%d').date()
        
        # Check if date_of_submission is before today's date
        if date_of_submission < datetime.now().date():
            context['msg'] = 'Due date cannot be before today'
            return render(request, 'faculty/FacultyAddAss.html', context)

        # Fetch the semester object
        semester = Semesters.objects.get(id=semester_id)
        
        # Fetch the subject object
        subject_obj = FacultySubject.objects.get(subject=subject)

        # Create and save the faculty assignment
        if assignment_no and date_of_submission and subject and assignment_question:
            faculty_assignment = FacultyAssignment(
                faculty=faculty,
                assignment_no=assignment_no,
                date_of_submission=date_of_submission,
                subject=subject_obj,
                assignment_question=assignment_question,
                Sem=semester
            )
            faculty_assignment.save()
            return redirect('FacultyAssignments')

    return render(request, 'faculty/FacultyAddAss.html', context)
def faculty_view_assignments(request):
    faculty = Faculty.objects.get(user=request.user)
    subjects = FacultySubject.objects.filter(faculty=faculty)
    assignments = FacultyAssignment.objects.filter(subject__in=subjects.values('subject'))
    student_assignments = StudentAssignment.objects.filter(assignment__in=assignments)
    context = {
        'assignments': assignments,
        'student_assignments': student_assignments,
        'faculty': faculty,
    }
    return render(request, 'faculty/FacultyViewAssignments.html', context)
def approve_or_reject_assignment(request, assignment_id, action):
    assignment = get_object_or_404(FacultyAssignment, pk=assignment_id)
    if action == 'approve':
        assignment.status = 'Approved'
        assignment.save()

        student_assignments = assignment.studentassignment_set.all()
        for student_assignment in student_assignments:
            student_assignment.status = 'Approved'
            student_assignment.save()

    elif action == 'reject':
        assignment.status = 'Rejected'
        assignment.save()

        student_assignments = assignment.studentassignment_set.all()
        for student_assignment in student_assignments:
            student_assignment.status = 'Rejected'
            student_assignment.save()
    else:
        pass  
    return redirect('faculty_view_assignments')
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(FacultyAssignment, id=assignment_id)
    assignment.delete()
    return redirect('FacultyAssignments')
def FacultyAddInternal(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    internal_marks = InternalMarks.objects.get(marks_std=student)

    context = {
        'student': student,
        'internal_marks': internal_marks,
    }

    return render(request, 'FacultyAddInternal.html', context)
def facultyAssignments(request):
    faculty = Faculty.objects.get(user = request.user)
    print(faculty)
    print(faculty.id)
    assignments = FacultyAssignment.objects.filter(faculty=faculty.id)
    print(assignments)
    context = {
        'faculty': faculty,
        'assignments': assignments,
    }

    return render(request, 'faculty/FacultyAssignments.html', context)
def edit_marks(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    faculty = get_object_or_404(Faculty, user=request.user)
    Psubjects = Subject.objects.filter(sem=student.Sem.semester)
    Imarks = InternalMarks.objects.filter(marks_std=student)

    if request.method == 'POST':
        for subject in Psubjects:
            sub_id = request.POST.get(f'sub_{subject.id}')
            # Get marks for the current subject
            ass1 = request.POST.get(f'ass1_{subject.id}')
            ass2 = request.POST.get(f'ass2_{subject.id}')
            ass3 = request.POST.get(f'ass3_{subject.id}')
            tp1 = request.POST.get(f'tp1_{subject.id}')
            
            # Calculate total marks
            total_marks = int(ass1 or 0) + int(ass2 or 0) + int(ass3 or 0) + int(tp1 or 0)

            # Get or create InternalMarks object for the current subject and student
            marks, created = InternalMarks.objects.get_or_create(marks_std=student, subject=subject)

            # Update marks
            marks.ass1 = ass1
            marks.ass2 = ass2
            marks.ass3 = ass3
            marks.tp1 = tp1
            marks.total = total_marks
            marks.save()

        return redirect('FacultyInternal')
    
    data = zip(Psubjects, Imarks)

    context = {
        'student': student,
        'data': data,
    }

    return render(request, 'faculty/edit_marks.html', context)

def FacultyEditProfile(request, faculty_id):
    faculty = Faculty.objects.get(id=faculty_id)

    if request.method == 'POST':
        faculty.user.first_name = request.POST.get('first_name')
        faculty.user.last_name = request.POST.get('last_name')
        faculty.Faculty_Dob = request.POST.get('dob')
        faculty.Faculty_Doj = request.POST.get('doj')
        faculty.Faculty_Department = request.POST.get('department')
        faculty.Faculty_Designation = request.POST.get('designation')
        faculty.Faculty_PhoneNUm = request.POST.get('phone_num')

        if request.FILES.get('profile_pic'):
            faculty.Faculty_Profile = request.FILES['profile_pic']
        faculty.user.save()  
        faculty.save()
    return render(request, 'faculty/FacultyEditProfile.html', {'faculty': faculty})
def remove_student(request, student_id):
    if request.method == 'POST':

        student = get_object_or_404(Student, pk=student_id)
        

        student.Is_Active = 'Terminated'

        student.save()
        
        # Redirect to a success page or any other desired URL
        return redirect('FacultyStudents')  # Replace 'success_page' with the desired URL name

    # Handle cases where the request method is not POST
    # You can return an error page or redirect to another URL
    return redirect('FacultyStudents')

# Students
def StudentReg(request):
    departments = Departments.objects.all()
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        password = request.POST.get('pass')
        password2 = request.POST.get('pass2')
        email = request.POST.get('email')
        Student_Dob = request.POST.get('dob')
        Student_Doj = date.today()
        Department = request.POST.get('department')
        Student_PhoneNUm = request.POST.get('pnum')
        Student_Profile = request.FILES.get('profile')

        Student_Department = Departments.objects.get(pk=Department)

        if password != password2:
            context = {
                'msg':'password doesnt match',
                'departments':departments
            }
            return render(request,'student/StudentReg.html',context)
        else:
            if Student.objects.filter(user__username = username).exists():
                context = {
                'msg':'username already exists',
                'departments':departments
            }
                return render(request,'student/StudentReg.html',context)

            if Student.objects.filter(user__email = email).exists():
                context = {
                'msg':'email already exists',
                'departments':departments
            }
                return render(request,'student/StudentReg.html',context)
            else:
                sem = Semesters.objects.get(pk=1)
                user = User.objects.create_user(username=username, password=password, email=email , first_name = firstname , last_name = lastname)
                Student.objects.create(user=user,Student_Dob = Student_Dob , Student_Department = Student_Department , Student_PhoneNum = Student_PhoneNUm , Student_Profile = Student_Profile , Sem=sem)
                return HttpResponseRedirect(reverse('StudentReg') + '?success=1')
    return render(request,'student/StudentReg.html',{'departments':departments})
def studentDash(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'student/StudentDash.html', {'error_message': 'Student not found'})

    context = {'student': student}
    return render(request, 'student/StudentDash.html', context)
def studentAttendance(request):
    try:
        student = Student.objects.get(user=request.user)
        attendances = StudentAttendance.objects.filter(student=student)
        present_days_count = attendances.filter(status='present').count()
    except Student.DoesNotExist:
        return render(request, 'student/StudentAttendance.html', {'error_message': 'Student not found'})

    context = {
        'student': student,
        'attendances': attendances,
        'present_days_count': present_days_count,
    }

    return render(request, 'student/StudentAttendance.html', context)
def studentStudents(request):
    return render(request,'student/StudentStudents.html')
def studentAssignments(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'student/StudentAssignments.html', {'error_message': 'Student not found'})

    student_semester = student.Sem
    print(student_semester)
    sem = Semesters.objects.get(pk = student_semester.id)
    faculty_assignments = FacultyAssignment.objects.filter(Sem=sem.id)
    student_submissions = StudentAssignment.objects.filter(student=student, assignment__in=faculty_assignments)
    submitted_assignment_ids = student_submissions.values_list('assignment_id', flat=True)
    not_submitted_assignments = faculty_assignments.exclude(id__in=submitted_assignment_ids)
    rejected_assignments = StudentAssignment.objects.filter(student=student, status='Rejected')
    student_assignments = not_submitted_assignments | FacultyAssignment.objects.filter(id__in=rejected_assignments.values_list('assignment_id', flat=True))
    context = {'student': student, 'student_assignments': student_assignments}
    return render(request, 'student/StudentAssignments.html', context)
def submit_assignment(request, assignment_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        assignment = get_object_or_404(FacultyAssignment, pk=assignment_id)
        try:
            submission = StudentAssignment.objects.get(student=student, assignment=assignment)
            submission.answer = request.FILES['file']
            submission.date_submitted = timezone.now()
            submission.status = 'pending'
            submission.save()
        except StudentAssignment.DoesNotExist:
            submission = StudentAssignment.objects.create(
                student=student,
                assignment=assignment,
                date_submitted=timezone.now(),
                answer=request.FILES['file'],
                status='pending'
            )
        assignment.status = 'pending'
        assignment.save()

    return redirect('studentAssignments')
def studentNotes(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'student/StudentNotes.html', {'error_message': 'Student not found'})
    student_department_notes = FacultyNotes.objects.filter(faculty__Faculty_Department=student.Student_Department)

    context = {'student': student, 'student_department_notes': student_department_notes}
    return render(request, 'student/StudentNotes.html', context)
def studentInternal(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'student/StudentInternal.html', {'error_message': 'Parent not found'})
    except Student.DoesNotExist:
        return render(request, 'student/StudentInternal.html', {'error_message': 'Student not found'})

    if student.Sem.semester == 1 or student.Sem.semester == 2:
        startsem = 1
        endsem = 2
    elif student.Sem.semester == 3 or student.Sem.semester == 4:
        startsem = 3
        endsem = 4
    elif student.Sem.semester == 5 or student.Sem.semester == 6:
        startsem = 5
        endsem = 6

    Psubjects = Subject.objects.filter(sem__in=range(startsem, endsem + 1))
    Imarks = InternalMarks.objects.filter(marks_std=student,subject__in=Psubjects)
    data = zip(Psubjects,Imarks)
    print(student)
    context = {'student': student, 'internal_marks': Imarks,'data': data,'subjects':Psubjects}
    return render(request, 'student/StudentInternal.html', context)
def studentLeave(request):
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'student/StudentLeave.html', {'error_message': 'Student not found'})
    try:
        leaveLetter = StudentLeaveLetter.objects.filter(leave_Student=student)
        # Proceed with handling the leave letter object
        # For example, you can access leaveLetter.leave_date, leaveLetter.reason, etc.
    except StudentLeaveLetter.DoesNotExist:
            leaveLetter = None 

    if request.method == 'POST':
        if 'submit' in request.POST:
            name = student.user.first_name
            date = request.POST.get('date')
            reason = request.POST.get('reason')
            nod = request.POST.get('nod')
            if student.Sem.semester==1 or student.Sem.semester==2:
                tutor='tutor1'
            elif student.Sem.semester==3 or student.Sem.semester==4:
                tutor='tutor2'
            elif student.Sem.semester==5 or student.Sem.semester==6:
                tutor='tutor3'
            try:
                parent = Parent.objects.get(stdParent=student)
            except:
                return render(request,'student/StudentLeave.html',{'msg':'Parent Doesnt Exists'})
            faculty = Faculty.objects.get(Faculty_Department=student.Student_Department,role=tutor)

            leave_letter = StudentLeaveLetter.objects.create(
                leave_Parent=parent,
                leave_faculty=faculty,
                leave_Student=student,
                reason=reason,
                date=date,
                isApproved="False"
            )

            subject = 'Leave Letter Submitted by {}'.format(student.user.first_name)
            message = '{} send a leave request for {}'.format(student.user.first_name, leave_letter.date)
            parent_email = parent.user.email
            send_mail(subject, message, 'sampleproject2211@gmail.com', [parent_email], fail_silently=False)
        # Initialize leaveLetter to None

            try:
                leaveLetter = StudentLeaveLetter.objects.filter(leave_Student=student)
                # Proceed with handling the leave letter object
                # For example, you can access leaveLetter.leave_date, leaveLetter.reason, etc.
            except StudentLeaveLetter.DoesNotExist:
                pass  # No need to do anything if the leave letter doesn't exist

    context = {
        'student': student,
        'leaveLetter': leaveLetter,
    }
    
    return render(request, 'student/StudentLeave.html', context)
def StudentEditProfile(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        user = student.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()

        student.Student_Dob = request.POST.get('Student_Dob', '')
        student.AdmissionNo = request.POST.get('AdmissionNo', '')
        student.Student_PhoneNum = request.POST.get('Student_PhoneNum', '')
        student.Student_Profile = request.FILES.get('profile_picture', student.Student_Profile)
        student.save()

    return render(request, 'student/StudentEditProfile.html', {'student': student})
def DelStdLeave(request,id):
        # Assuming StudentLeaveLetter is your model name
    try:
        # Get the student leave item to delete
        leave_item = StudentLeaveLetter.objects.get(id=id)
        # Delete the item from the database
        leave_item.delete()
        # Return a success response
        return redirect(studentLeave)
    except StudentLeaveLetter.DoesNotExist:
        pass
def ViewStudentProfile(request,id):
    student= Student.objects.get(pk=id)
    internals = InternalMarks.objects.filter(marks_std = student)
    attendance = StudentAttendance.objects.filter(student=student)
    count = attendance.filter(status='present').count()
    semesters = Semesters.objects.all()
    context = {
        'student':student,
        'internals':internals,
        'attendance':count,
        'semesters':semesters,
    }
    return render(request,'student/ViewStudentProfile.html',context)
# Parent
def ParentReg(request):
    students = Student.objects.all()
    context = {'students': students}

    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('Lastname')
        username = request.POST.get('username')
        admNo = request.POST.get('admNo')
        password = request.POST.get('pass')
        password2 = request.POST.get('pass2')
        email = request.POST.get('email')
        Parent_PhoneNUm = request.POST.get('pnum')
        Parent_Profile = request.FILES.get('profile')

        if password != password2:
            context['msg'] = 'Password does not match'
            return render(request, 'parent/parentReg.html', context)
        if User.objects.filter(username=username).exists():
            context['msg'] = 'Username already exists'
            return render(request, 'parent/parentReg.html', context)

        if Parent.objects.filter(user__email=email).exists():
            context['msg'] = 'Email already exists'
            return render(request, 'parent/parentReg.html', context)

        try:
            stud = Student.objects.get(AdmissionNo=admNo)
        except Student.DoesNotExist:
            context['msg'] = 'Student with admission number {} does not exist.'.format(admNo)
            return render(request, 'parent/parentReg.html', context)
        user = User.objects.create_user(username=username, password=password, email=email,
                                        first_name=firstname, last_name=lastname)

        Parent_Name = str(firstname) + " " + str(lastname)
        Parent.objects.create(user=user, Parent_Name=Parent_Name, Parent_num=Parent_PhoneNUm,
                               Parent_Profile=Parent_Profile, stdParent=stud , AdmissionNo=admNo)

        return render(request, 'parent/ParentReg.html', context)

    return render(request, 'parent/ParentReg.html', context)
def ParentDash(request):
    try:
        parent = Parent.objects.get(user=request.user)
        student = Student.objects.get(AdmissionNo=parent.AdmissionNo)
    except Parent.DoesNotExist:
        parent = None
        student = None
    except Student.DoesNotExist:
        student = None

    context = {'parent': parent, 'student': student}
    return render(request, 'parent/ParentDash.html', context)
def ParentAttendance(request):
    try:
        parent = Parent.objects.get(user=request.user)
        student = Student.objects.get(AdmissionNo=parent.AdmissionNo)
        attendance_details = StudentAttendance.objects.filter(student=student)
        present_days_count = attendance_details.filter(status='present').count()
    except (Parent.DoesNotExist, Student.DoesNotExist):
        parent = None
        student = None
        attendance_details = None
        present_days_count = 0

    context = {
        'parent': parent,
        'student': student,
        'attendance_details': attendance_details,
        'present_days_count': present_days_count,
    }
    return render(request, 'parent/ParentAttendance.html', context)
def ParentStudents(request):
    return render(request,'parent/ParentStudents.html')
def ParentAssignments(request):
    try:
        parent = Parent.objects.get(user=request.user)
        student = Student.objects.get(AdmissionNo=parent.AdmissionNo)
        faculties = Faculty.objects.filter(Faculty_Department=student.Student_Department)
        department_assignments = FacultyAssignment.objects.filter(faculty__in=faculties)
        assignments_with_status = {}
        for assignment in department_assignments:
            is_submitted = StudentAssignment.objects.filter(assignment=assignment, student=student).exists()
            assignments_with_status[assignment] = is_submitted
            
    except (Parent.DoesNotExist, Student.DoesNotExist):
        parent = None
        student = None
        assignments_with_status = {}
    context = {'parent': parent, 'student': student, 'assignments_with_status': assignments_with_status}
    return render(request, 'parent/ParentAssignments.html', context)
def ParentNotes(request):
    try:
        parent = Parent.objects.get(user=request.user)
        student = Student.objects.get(AdmissionNo=parent.AdmissionNo)
        department_notes = FacultyNotes.objects.filter(faculty__Faculty_Department=student.Student_Department)
        return render(request, 'parent/ParentNotes.html', {'notes': department_notes,'parent':parent})
    
    except (Parent.DoesNotExist, Student.DoesNotExist) as e:
        return render(request, 'error.html', {'error_message': str(e)})
def ParentInternal(request):
    try:
        parent = Parent.objects.get(user=request.user)
        student = Student.objects.get(AdmissionNo=parent.AdmissionNo)
    except Parent.DoesNotExist:
        return render(request, 'parent/parentInternal.html', {'error_message': 'Parent not found'})
    except Student.DoesNotExist:
        return render(request, 'parent/parentInternal.html', {'error_message': 'Student not found'})

    if student.Sem.semester == 1 or student.Sem.semester == 2:
        startsem = 1
        endsem = 2
    elif student.Sem.semester == 3 or student.Sem.semester == 4:
        startsem = 3
        endsem = 4
    elif student.Sem.semester == 5 or student.Sem.semester == 6:
        startsem = 5
        endsem = 6

    Psubjects = Subject.objects.filter(sem__in=range(startsem, endsem + 1))
    Imarks = InternalMarks.objects.filter(marks_std=student,subject__in=Psubjects)
    data = zip(Psubjects,Imarks)
    print(student)
    context = {'student': student, 'internal_marks': Imarks,'parent':parent,'data': data,'subjects':Psubjects}
    return render(request, 'parent/ParentInternal.html', context)
def ParentLeaveLetter(request):
    parent = Parent.objects.get(user=request.user)
    student = Student.objects.get(AdmissionNo=parent.AdmissionNo)
    student_leave_letters = StudentLeaveLetter.objects.filter(Q(leave_Parent=parent) & Q(isApprovedParent=False))
    context = {
        'student_leave_letters': student_leave_letters,
        'parent' : parent,
    }
    return render(request, 'parent/ParentLeaveApproval.html', context)
def approve_reject_leave(request, leave_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        leave_letter = StudentLeaveLetter.objects.get(id=leave_id)

        if status == 'approve':
            leave_letter.isApprovedParent = True
        elif status == 'reject':
            leave_letter.isApprovedParent = 'rejected'

        leave_letter.save()

        if leave_letter.isApprovedParent:
            parent = Parent.objects.get(user=request.user)
            student = Student.objects.get(AdmissionNo=parent.AdmissionNo)
            department = student.Student_Department
            faculty = Faculty.objects.filter(Faculty_Department=department).first()
            if faculty:
                subject = 'Leave Letter Submitted by {}'.format(student.user.first_name)
                message = '{} sent a leave request for {}'.format(student.user.first_name, leave_letter.date)
                faculty_email = faculty.user.email
                send_mail(subject, message, 'sampleproject2211@gmail.com', [faculty_email], fail_silently=False)
                recipient_email = faculty.user.email

    return redirect('ParentLeaveLetter')
