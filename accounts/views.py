from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RoleSelectionForm, DoctorSignupForm, PatientSignupForm
from .models import User, PatientProfile, DoctorProfile
from gync.models import Appointment
from gync.models import Doctor  # Fetch doctor data
from patient.models import Patient  # Fetch patient data
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        # Get username and password from the POST data
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        # Query the database to get the user's hashed password
        with connection.cursor() as cursor:
            # The query to select the user based on username
            query = "SELECT password, role, id FROM accounts_user WHERE username = %s"
            cursor.execute(query, [username])
            result = cursor.fetchone()  # Fetch one matching record

        if result is not None:
            stored_password_hash = result[0]
            role = result[1].strip().lower()
            user_id = result[2]

            # Use Django's check_password function to verify the password
            if check_password(password, stored_password_hash):
                user = User.objects.get(id=user_id)
                login(request, user)
                if role == 'doctor':
                    print("Redirecting to doctor dashboard")
                    return redirect('doctor_dashboard')
                elif role == 'patient':
                    print("Redirecting to patient dashboard")
                    return redirect('patient_dashboard')
                else:
                    print("Role not recognized")
                    messages.error(request, "User role is not recognized.")
                    return render(request, 'accounts/login.html')
            else:
                print("Incorrect password")
                messages.error(request, "Incorrect password!")
                return render(request, 'accounts/login.html')
        else:
            print("User not found")
            messages.error(request, "User not found!")
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')

def edit_patient_profile(request):
    """Handle editing of a patient's profile"""

    profile, created = PatientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PatientSignupForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = PatientSignupForm(instance=profile)

    return render(request, 'accounts/edit_patient_profile.html', {'form': form})


def select_role_view(request):
    """Step 1: Ask for the role"""
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            return redirect('signup_step2', role=role)
    else:
        form = RoleSelectionForm()
    return render(request, 'accounts/select_role.html', {'form': form})

#priyanka
def recommend_doctor_view(request):
    """Fetch specializations and doctors based on selection"""
    # Get distinct specializations from the database
    specializations = DoctorProfile.objects.values_list('specialization', flat=True).distinct()

    # Get selected specialization from user input
    selected_specialization = request.GET.get('specialization', '')

    # Fetch doctors based on the selected specialization
    doctors = DoctorProfile.objects.filter(specialization=selected_specialization) if selected_specialization else []

    return render(request, 'accounts/recommend_doctor.html', {
        'specializations': specializations,
        'doctors': doctors,
        'selected_specialization': selected_specialization
    })


def signup_view(request, role):
    """Step 2: Show appropriate signup form based on role"""
    if role not in ['doctor', 'patient']:
        return redirect('select_role')

    if request.method == 'POST':
        if role == 'doctor':
            form = DoctorSignupForm(request.POST)
        else:
            form = PatientSignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = role
            user.save()

            if role == 'doctor':
                DoctorProfile.objects.create(user=user, registration_number=form.cleaned_data['registration_number'],specialization=form.cleaned_data['specialization'])
            else:
                PatientProfile.objects.create(user=user, age=form.cleaned_data['age'])

            login(request, user)

            # Redirect based on role
            if role == 'doctor':
                return redirect('doctor_dashboard')  
            else:
                return redirect('patient_dashboard')  

    else:
        form = DoctorSignupForm() if role == 'doctor' else PatientSignupForm()

    return render(request, 'accounts/signup.html', {'form': form, 'role': role})


# def signup_view(request, role):
#     """Step 2: Show appropriate signup form based on role using SQL queries"""
#     if role not in ['doctor', 'patient']:
#         return redirect('select_role')

#     if request.method == 'POST':
#         if role == 'doctor':
#             form = DoctorSignupForm(request.POST)
#         else:
#             form = PatientSignupForm(request.POST)

#         if form.is_valid():
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email']
#             password1 = form.cleaned_data['password1']
#             password2 = form.cleaned_data['password2']

#             # SQL Insert Query for creating a User with necessary fields
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO accounts_user (username, email, password, role, is_superuser, is_staff, date_joined)
#                     VALUES (%s, %s, %s, %s, %s, %s, NOW())
#                 """, [username, email, password1, role, False, False])  # Set is_superuser and is_staff to False

#             # Fetch the last inserted user_id
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT id FROM accounts_user WHERE username = %s", [username])
#                 user_id = cursor.fetchone()[0]

#             # Create Doctor or Patient Profile using raw SQL Insert
#             if role == 'doctor':
#                 registration_number = form.cleaned_data['registration_number']
#                 specialization = form.cleaned_data['specialization']
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         INSERT INTO doctor_table (user_id, registration_number, specialization)
#                         VALUES (%s, %s, %s)
#                     """, [user_id, registration_number, specialization])

#             elif role == 'patient':
#                 age = form.cleaned_data['age']
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         INSERT INTO accounts_patient_profile_table (user_id, age, is_private)
#                         VALUES (%s, %s, 0)  -- Setting is_private to 0 by default
#                     """, [user_id, age])

#             # After saving, log the user in
#             user = User.objects.get(id=user_id)
#             login(request, user)

#             # Redirect based on role
#             if role == 'doctor':
#                 return redirect('doctor_dashboard')  
#             else:
#                 return redirect('patient_dashboard')  

#     else:
#         form = DoctorSignupForm() if role == 'doctor' else PatientSignupForm()

#     return render(request, 'accounts/signup.html', {'form': form, 'role': role})




@login_required
def profile_view(request):
    """View to render the profile page based on user role using SQL queries."""
    user = request.user  # Get the logged-in user
    profile_data = {}

    with connection.cursor() as cursor:
        if user.role == 'patient':
            # Fetch patient details from accounts_patient_profile_table
            cursor.execute("""
                SELECT age, is_private 
                FROM accounts_patient_profile_table 
                WHERE user_id = %s
            """, [user.id])
            row = cursor.fetchone()
            if row:
                profile_data = {
                    "age": row[0],
                    "is_private": row[1],
                }
        elif user.role == 'doctor':
            # Fetch doctor details from doctor_table
            cursor.execute("""
                SELECT registration_number, specialization 
                FROM doctor_table 
                WHERE user_id = %s
            """, [user.id])
            row = cursor.fetchone()
            if row:
                profile_data = {
                    "registration_number": row[0],
                    "specialization": row[1],
                }

    return render(request, 'accounts/profile.html', {'profile': profile_data})
