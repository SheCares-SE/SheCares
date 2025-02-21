from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login, authenticate,get_user_model
from .forms import RoleSelectionForm, DoctorSignupForm, PatientSignupForm
from .models import User, PatientProfile, DoctorProfile
from gync.models import DoctorProfile # Fetch doctor data
from patient.models import Patient  # Fetch patient data
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import check_password , make_password
from django.contrib import messages
from django.db import connection
from django.contrib.auth.decorators import login_required
from .models import Question, Answer
from django.utils.timezone import now
from django.utils import timezone
from django.http import HttpResponse  # Add this import
from django.urls import reverse

# Aishna
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
                    return redirect('gync:doctor_dashboard')
                elif role == 'patient':
                    print("Redirecting to patient dashboard")
                    return redirect('patient:patient_dashboard')
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

#aishna
def select_role_view(request):
    """Step 1: Ask for the role"""
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            return redirect('accounts:signup', role=role)

    else:
        form = RoleSelectionForm()
    return render(request, 'accounts/select_role.html', {'form': form})

#priyanka
# def recommend_doctor_view(request):
#     """Fetch specializations and doctors based on selection"""
#     # Get distinct specializations from the database
#     specializations = DoctorProfile.objects.values_list('specialization', flat=True).distinct()

#     # Get selected specialization from user input
#     selected_specialization = request.GET.get('specialization', '')

#     # Fetch doctors based on the selected specialization
#     doctors = DoctorProfile.objects.filter(specialization=selected_specialization) if selected_specialization else []

#     return render(request, 'accounts/recommend_doctor.html', {
#         'specializations': specializations,
#         'doctors': doctors,
#         'selected_specialization': selected_specialization
#     })

def recommend_doctor_view(request):
    """Fetch specializations and doctors based on selection using raw MySQL queries"""

    with connection.cursor() as cursor:
        # Get distinct specializations from the database
        cursor.execute("SELECT DISTINCT specialization FROM doctor_table")
        specializations = [row[0] for row in cursor.fetchall()]

        # Get selected specialization from user input
        selected_specialization = request.GET.get('specialization', '').lower()

        # Fetch doctors based on the selected specialization
        doctors = []
        if selected_specialization:
            cursor.execute("""
                SELECT accounts_user.username, doctor_table.registration_number, doctor_table.specialization
                FROM doctor_table
                JOIN accounts_user ON doctor_table.user_id = accounts_user.id
                WHERE doctor_table.specialization = LOWER(%s)
            """, [selected_specialization])
            
            doctors = cursor.fetchall()  # Returns list of tuples (username, registration_number, specialization)
    
    return render(request, 'accounts/recommend_doctor.html', {
        'specializations': specializations,
        'doctors': doctors,
        'selected_specialization': selected_specialization
    })

# Aishna
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
            user_data = form.cleaned_data
            user_role = role

            # Retrieve and hash the password separately
            password = request.POST.get('password1')  # Change to the correct field name in your form
            if not password:
                form.add_error('password1', 'Password is required.')
                return render(request, 'accounts/signup.html', {'form': form, 'role': role})

            hashed_password = make_password(password)

            # Insert user into the accounts_user table with necessary fields and default values
            date_joined = timezone.now()

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO accounts_user (username, email, password, first_name, last_name, is_superuser, is_staff, is_active, role, profile_picture, date_joined)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    user_data.get('username', 'default_username'), 
                    user_data.get('email', 'default@example.com'), 
                    hashed_password, 
                    user_data.get('first_name', 'First'), 
                    user_data.get('last_name', 'Last'), 
                    False, 
                    False, 
                    True, 
                    user_role,
                    user_data.get('profile_picture', ''),  # Assuming this field can be empty
                    date_joined
                ])
                
                # Get the inserted user ID
                cursor.execute("SELECT LAST_INSERT_ID()")
                user_id = cursor.fetchone()[0]

            if role == 'doctor':
                # Insert doctor profile into the doctor_table
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO doctor_table (user_id, registration_number, specialization)
                        VALUES (%s, %s, %s)
                    """, [user_id, user_data.get('registration_number', 'default_registration_number'), user_data.get('specialization', 'default_specialization')])
            else:
                # Insert patient profile into the accounts_patient_profile_table
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO accounts_patient_profile_table (user_id, age, is_private)
                        VALUES (%s, %s, %s)
                    """, [user_id, user_data.get('age', 30), user_data.get('is_private', False)])

            # Authenticate and login user
            user = User.objects.get(pk=user_id)
            login(request, user)

            # Redirect based on role
            if role == 'doctor':
                 return redirect(reverse('gync:doctor_dashboard'))
            else:
                 return redirect(reverse('patient:patient_dashboard'))
  

    else:
        form = DoctorSignupForm() if role == 'doctor' else PatientSignupForm()

    return render(request, 'accounts/signup.html', {'form': form, 'role': role})

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
                FROM patient_table 
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

#Urvashi
@login_required
def faq_page(request):
    if request.method == "POST":
        # Determine if a question or answer is being submitted
        if 'question_text' in request.POST:
            question_text = request.POST.get("question_text")
            if question_text:
                Question.objects.create(user=request.user, text=question_text)
                messages.success(request, "Question submitted successfully!")
            else:
                messages.error(request, "Question cannot be empty.")
        elif 'answer_text' in request.POST:
            question_id = request.POST.get("qus_id")
            answer_text = request.POST.get("answer_text")
            question = get_object_or_404(Question, qus_id=question_id)
            
            # Ensure only gynecologists can answer:
            if request.user.role == "doctor":
                if answer_text:
                    Answer.objects.create(user=request.user, qus=question, text=answer_text)
                    messages.success(request, "Answer submitted successfully!")
                else:
                    messages.error(request, "Answer cannot be empty.")
            else:
                messages.error(request, "Only gynecologists can answer questions.")
        return redirect("accounts:faq_page")

    questions = Question.objects.all().order_by("-created_at")
    return render(request, "accounts/faq.html", {"questions": questions})

@login_required
def add_question(request):
    # This view can be used for a separate "Add Question" page if needed.
    # For our one-page FAQ, the form is handled in faq_page.
    return redirect("accounts:faq_page")

@login_required
def add_answer(request, question_id):
    # This view is now handled in faq_page via POST data.
    return redirect("accounts:faq_page")

# @login_required
# def add_answer(request, question_id):
#     question = get_object_or_404(Question, qus_id=question_id)
    
#     # Check that the user has the doctor role (assuming doctor role is stored as "doctor")
#     if request.user.role != "doctor":
#         messages.error(request, "Only doctors can answer questions.")
#         return redirect("faq_page")
    
#     if request.method == "POST":
#         answer_text = request.POST.get("answer_text")
#         if answer_text:
#             Answer.objects.create(user=request.user, qus=question, text=answer_text)
#             messages.success(request, "Answer submitted successfully!")
#         else:
#             messages.error(request, "Answer cannot be empty.")
#     return redirect("faq_page")


