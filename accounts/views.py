
import os
import logging
from django.contrib.auth import login,logout
from django.shortcuts import render, redirect , get_object_or_404
from django.db import connection,transaction
from SC import settings
from .forms import RoleSelectionForm, DoctorSignupForm, PatientSignupForm, ProfilePictureForm ,ProfileUpdateForm
from .models import User , Question, Answer
from django.contrib import messages
from django.contrib.auth.hashers import check_password , make_password
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse,JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


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
                city = user_data.get('city', 'Default City')
                opening_time = user_data.get('opening_time')
                closing_time = user_data.get('closing_time')
                break_start = user_data.get('break_start')
                break_end = user_data.get('break_end')

                # availability = user_data.get('availability', 'Defauly Time')  # Capture availability
                # Insert doctor profile into the doctor_table
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO doctor_table (user_id, registration_number, specialization, city, opening_time, closing_time, break_start, break_end)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, [user_id, user_data.get('registration_number', 'default_registration_number'), user_data.get('specialization', 'default_specialization'), city,opening_time,closing_time,break_start,break_end])

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


@login_required
def profile_view(request):
    """View to render the profile page based on user role using SQL queries."""
    user = request.user  # Get the logged-in user
    profile_data = {}
    feedback_list = []

    with connection.cursor() as cursor:
        if user.role == 'patient':
            # Fetch patient details
            cursor.execute("""
                SELECT u.username, p.age, u.role, u.profile_picture 
                FROM accounts_user u
                JOIN accounts_patient_profile_table p ON u.id = p.user_id
                WHERE u.id = %s
            """, [user.id])
            row = cursor.fetchone()
            if row:
                profile_data = {
                    "profile_picture": row[3] if row[3] else None,
                    "username": row[0],  # Keeping username as per your schema
                    "age": row[1],
                    "role": row[2],
                }

        elif user.role == 'doctor':
            # Fetch doctor details
            cursor.execute("""
                SELECT d.registration_number, d.specialization, u.username, u.profile_picture ,  d.city, d.opening_time, d.closing_time, d.break_start, d.break_end
                FROM doctor_table d
                INNER JOIN accounts_user u ON d.user_id = u.id
                WHERE d.user_id = %s
            """, [user.id])
            row = cursor.fetchone()
            # print("Doctor Profile Data:", row)
            if row:
                profile_data = {
                    "profile_picture": row[3] if row[3] else None,
                    "username": row[2],  # Keeping username as per your schema
                    "registration_number": row[0],
                    "specialization": row[1],
                    "city": row[4],
                    # "availability": row[5]
                    "opening_time": row[5],
                    "closing_time": row[6],
                    "break_start": row[7],
                    "break_end": row[8]
                }

            # Fetch average rating
            cursor.execute("""
                SELECT ROUND(AVG(rating),1) AS avg_rating
                FROM doctor_feedback
                WHERE doctor_id = %s
            """, [user.id])
            avg_rating = cursor.fetchone()
            profile_data["avg_rating"] = avg_rating[0] if avg_rating else "No ratings yet"


            cursor.execute("""
                SELECT df.feedback, df.rating, au.username
                FROM doctor_feedback df
                JOIN accounts_user au ON df.patient_id = au.id
                WHERE df.doctor_id = %s
                ORDER BY df.created_at DESC;
            """, [user.id])
            formatted_feedback_list = [
                {
                    "feedback": row[0],
                    "rating": row[1],
                    "patient_name": row[2]
                } for row in cursor.fetchall()
            ]
            profile_data["feedback_list"] = formatted_feedback_list

    form = ProfilePictureForm()

    return render(request, 'accounts/profile.html', {'profile': profile_data, 'form': form})


@login_required
def upload_profile_picture(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile_view')  # Redirect to profile after upload

    return redirect('accounts:profile_view')


@login_required
def remove_profile_picture(request):
    user = request.user
    if user.profile_picture:
        user.profile_picture.delete()
        user.profile_picture = None
        user.save()
    return redirect('accounts:profile_view')


@login_required
def edit_profile(request):
    user = request.user
    user_type = None
    initial_data = {}

    # Fetch user-specific details
    if user.role == 'doctor':  # If user is a doctor
        user_type = 'doctor'
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT d.registration_number, d.specialization, a.username, d.city, 
                    d.opening_time, d.closing_time, d.break_start, d.break_end
                FROM doctor_table d 
                JOIN accounts_user a ON a.id = d.user_id
                WHERE d.user_id = %s
            """, [user.id])
            row = cursor.fetchone()
            if row:
                initial_data = {
                    'registration_number': row[0],
                    'specialization': row[1],
                    'username': row[2],
                    'city': row[3],
                    'opening_time': row[4].strftime('%H:%M:%S') if row[4] else None,
                    'closing_time': row[5].strftime('%H:%M:%S') if row[5] else None,
                    'break_start': row[6].strftime('%H:%M:%S') if row[6] else None,
                    'break_end': row[7].strftime('%H:%M:%S') if row[7] else None,
                }

    elif user.role == 'patient':  # If user is a patient
        user_type = 'patient'
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.age, u.username
                FROM accounts_user u
                JOIN accounts_patient_profile_table p ON u.id = p.user_id
                WHERE u.id = %s
            """, [user.id])
            row = cursor.fetchone()
            if row:
                initial_data['age'] = row[0]

    # Fetch existing profile picture
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT profile_picture 
            FROM accounts_user 
            WHERE id = %s
        """, [user.id])
        row = cursor.fetchone()
        if row and row[0]:
            initial_data['profile_picture'] = row[0]  

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, user_type=user_type)
        if form.is_valid():
            profile_picture = form.cleaned_data.get('profile_picture')

            # Update profile picture only if a new one is uploaded
            if profile_picture:
                file_path = os.path.join(settings.MEDIA_ROOT, profile_picture.name)
                profile_picture_path = f"profile_pictures/{profile_picture.name}"  # Adjust path as needed
                with open(file_path, 'wb+') as destination:
                    for chunk in profile_picture.chunks():
                        destination.write(chunk)
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE accounts_user
                        SET profile_picture = %s
                        WHERE id = %s
                    """, [profile_picture_path, user.id]) # Store filename/path instead of file object

            # Update doctor_table if user is a doctor
            if user_type == 'doctor':
                registration_number = form.cleaned_data.get('registration_number')
                specialization = form.cleaned_data.get('specialization')
                username = form.cleaned_data.get('username')
                city = form.cleaned_data.get('city')
                opening_time = form.cleaned_data.get('opening_time')
                closing_time = form.cleaned_data.get('closing_time')
                break_start = form.cleaned_data.get('break_start')
                break_end = form.cleaned_data.get('break_end')
                # availability = form.cleaned_data.get('availability')
                # with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE doctor_table 
                        SET registration_number = %s, specialization = %s, city = %s, opening_time=%s, closing_time=%s,break_start=%s, break_end=%s
                        WHERE user_id = %s
                     """, [registration_number, specialization,city,opening_time,closing_time,break_start,break_end, user.id])
                    connection.commit()

    # Update accounts_user (username)
                    cursor.execute("""
                            UPDATE accounts_user
                            SET username = %s
                            WHERE id = %s
                    """, [username, user.id])

            # Update patient_table if user is a patient
            elif user_type == 'patient':
                age = form.cleaned_data.get('age')
                username = form.cleaned_data.get('username')
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE accounts_patient_profile_table
                        SET age = %s
                        WHERE user_id = %s
                    """, [age, user.id])
                    cursor.execute("""
                        UPDATE accounts_user
                        SET username = %s
                        WHERE id = %s
                    """, [username, user.id])
            user.save()
            return redirect('accounts:profile_view')   # Redirect to the profile page

        else:
            print("Form errors:", form.errors)  # Add this line
            messages.error(request, "Error updating profile. Please check your inputs.")

    else:
        form = ProfileUpdateForm(user_type=user_type, initial=initial_data)

    return render(request, 'accounts/edit_profile.html', {'form': form, 'user_type': user_type})


@login_required
def doctor_profile(request, doctor_id):
    with connection.cursor() as cursor:
        # Fetch doctor details
        cursor.execute("""
            SELECT u.username, u.last_name, d.specialization, d.city , d.opening_time, d.closing_time, d.break_start, d.break_end
            FROM doctor_table d
            JOIN accounts_user u ON d.user_id = u.id
            WHERE d.user_id = %s
        """, [doctor_id])
        doctor = cursor.fetchone()


        if not doctor:
            return HttpResponse("Doctor not found", status=404)

        # Fetch feedback
        cursor.execute("""
            SELECT df.feedback, df.rating, u.username
            FROM doctor_feedback df
            JOIN accounts_user u ON df.patient_id = u.id
            WHERE df.doctor_id = %s
        """, [doctor_id])
        feedback_list = cursor.fetchall()

        # Calculate average rating
        cursor.execute("""
            SELECT COALESCE(AVG(rating), 0)
            FROM doctor_feedback
            WHERE doctor_id = %s
        """, [doctor_id])
        avg_rating = cursor.fetchone()[0]

    context = {
        "username": doctor[0],
        "last_name": doctor[1],
        "specialization": doctor[2],
        "city": doctor[3],
        "opening_time": doctor[4],
        "closing_time": doctor[5],
        "break_start": doctor[6],
        "break_end": doctor[7],
        "avg_rating": avg_rating,
        "feedback_list": feedback_list,
        "doctor_id": doctor_id
    }
    return render(request, 'accounts/doctor_profile.html', context)


@login_required
def recommend_doctor_view(request):
    # Fetch doctors with distinct cities and specializations 
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT city FROM doctor_table WHERE city IS NOT NULL")
        cities = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT specialization FROM doctor_table WHERE specialization IS NOT NULL")
        specializations = [row[0] for row in cursor.fetchall()]

    # Get filter parameters from the request
    selected_city = request.GET.get('city', '')
    selected_specialization = request.GET.get('specialization', '')

    # Fetch doctors based on filters
    query = """
        SELECT au.id, au.username, dt.registration_number, dt.specialization, dt.city
        FROM accounts_user au
        JOIN doctor_table dt ON au.id = dt.user_id
        WHERE au.role = 'doctor'
    """
    params = []

    if selected_city:
        query += " AND dt.city = %s"
        params.append(selected_city)
    if selected_specialization:
        query += " AND dt.specialization = %s"
        params.append(selected_specialization)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        doctors = cursor.fetchall()

    context = {
        'cities': cities,
        'specializations': specializations,
        'selected_city': selected_city,
        'selected_specialization': selected_specialization,
        'doctors': doctors,
    }
    return render(request, 'accounts/recommend_doctor.html', context)


@login_required
def submit_feedback(request, doctor_id):
    if request.method == "POST":
        rating = request.POST.get("rating")
        feedback = request.POST.get("feedback")
        patient_id = request.user.id  # Logged-in patient ID

        with connection.cursor() as cursor:
            # Check if feedback already exists
            cursor.execute("""
                SELECT 1 FROM doctor_feedback 
                WHERE doctor_id = %s AND patient_id = %s
            """, [doctor_id, patient_id])
            exists = cursor.fetchone()

            if exists:
                messages.warning(request, "You have already submitted feedback for this doctor.")
                return redirect('accounts:doctor_profile', doctor_id=doctor_id)

            # Insert feedback
            cursor.execute("""
                INSERT INTO doctor_feedback (doctor_id, patient_id, rating, feedback, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, [doctor_id, patient_id, rating, feedback])

            messages.success(request, "Feedback submitted successfully!")

        return redirect('accounts:doctor_profile', doctor_id=doctor_id)

    return redirect('accounts:recommend_doctor')


@login_required
def faq_page(request):
    if request.method == "POST":
        cursor = connection.cursor()
        # If a new question is submitted:
        if 'question_text' in request.POST:
            question_text = request.POST.get("question_text")
            if question_text:
                # Insert the question using raw SQL
                cursor.execute("""
                    INSERT INTO accounts_question (user_id, text, created_at, upvote_count)
                    VALUES (%s, %s, NOW(), 0)
                """, [request.user.id, question_text])
                # messages.success(request, "Question submitted successfully!")
            else:
                messages.error(request, "Question cannot be empty.")
        # If an answer is submitted:
        elif 'answer_text' in request.POST:
            question_id = request.POST.get("qus_id")
            answer_text = request.POST.get("answer_text")
            # Verify that the question exists
            cursor.execute("SELECT qus_id FROM accounts_question WHERE qus_id = %s", [question_id])
            if cursor.fetchone() is None:
                messages.error(request, "Question not found.")
            else:
                if request.user.role == "doctor":
                    if answer_text:
                        cursor.execute("""
                            INSERT INTO accounts_answer (qus_id, user_id, text, created_at, upvote_count)
                            VALUES (%s, %s, %s, NOW(), 0)
                        """, [question_id, request.user.id, answer_text])
                        # messages.success(request, "Answer submitted successfully!")
                    else:
                        messages.error(request, "Answer cannot be empty.")
                else:
                    messages.error(request, "Only doctors can answer questions.")
        return redirect("accounts:faq_page")
    questions = Question.objects.raw("""
        SELECT * FROM accounts_question
        ORDER BY upvote_count DESC, created_at DESC
    """)
    return render(request, "accounts/faq.html", {"questions": questions})


@login_required
def upvote_question(request):
    if request.method == "POST":
        user_id = request.user.id
        qus_id = request.POST.get("qus_id")
        cursor = connection.cursor()

        # Check if the user has already liked the question
        cursor.execute(
            "SELECT COUNT(*) FROM accounts_questionlike WHERE user_id = %s AND question_id = %s",
            [user_id, qus_id]
        )
        already_liked = cursor.fetchone()[0] > 0  # If count > 0, user has already liked

        if already_liked:
            # Unlike (remove like)
            cursor.execute(
                "DELETE FROM accounts_questionlike WHERE user_id = %s AND question_id = %s",
                [user_id, qus_id]
            )
            cursor.execute(
                "UPDATE accounts_question SET upvote_count = upvote_count - 1 WHERE qus_id = %s",
                [qus_id]
            )
            liked = False
        else:
            # Like (add like)
            cursor.execute(
                "INSERT INTO accounts_questionlike (user_id, question_id, created_at) VALUES (%s, %s, NOW())",
                [user_id, qus_id]
            )
            cursor.execute(
                "UPDATE accounts_question SET upvote_count = upvote_count + 1 WHERE qus_id = %s",
                [qus_id]
            )
            liked = True

        # Get updated like count
        cursor.execute("SELECT upvote_count FROM accounts_question WHERE qus_id = %s", [qus_id])
        new_count = cursor.fetchone()[0]

        return JsonResponse({"upvote_count": new_count, "liked": liked})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def upvote_answer(request):
    if request.method == "POST":
        user_id = request.user.id
        ans_id = request.POST.get("ans_id")
        cursor = connection.cursor()

        # Check if the user has already liked the answer
        cursor.execute(
            "SELECT COUNT(*) FROM accounts_answerlike WHERE user_id = %s AND answer_id = %s",
            [user_id, ans_id]
        )
        already_liked = cursor.fetchone()[0] > 0

        if already_liked:
            # Unlike (remove like)
            cursor.execute(
                "DELETE FROM accounts_answerlike WHERE user_id = %s AND answer_id = %s",
                [user_id, ans_id]
            )
            cursor.execute(
                "UPDATE accounts_answer SET upvote_count = upvote_count - 1 WHERE ans_id = %s",
                [ans_id]
            )
            liked = False
        else:
            # Like (add like)
            cursor.execute(
                "INSERT INTO accounts_answerlike (user_id, answer_id, created_at) VALUES (%s, %s, NOW())",
                [user_id, ans_id]
            )
            cursor.execute(
                "UPDATE accounts_answer SET upvote_count = upvote_count + 1 WHERE ans_id = %s",
                [ans_id]
            )
            liked = True

        # Get updated like count
        cursor.execute("SELECT upvote_count FROM accounts_answer WHERE ans_id = %s", [ans_id])
        new_count = cursor.fetchone()[0]

        return JsonResponse({"upvote_count": new_count, "liked": liked})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def add_question(request):

    return redirect("accounts:faq_page")

@login_required
def add_answer(request, question_id):
    return redirect("accounts:faq_page")

@login_required
def your_questions(request):
    # Questions the user asked:
    asked_questions = Question.objects.filter(user=request.user).order_by("-created_at")
    
    # Questions the user answered (distinct)
    answered_question_ids = Answer.objects.filter(user=request.user).values_list('qus__qus_id', flat=True).distinct()
    answered_questions = Question.objects.filter(qus_id__in=answered_question_ids).order_by("-created_at")
    
    return render(request, "accounts/your_questions.html", {
        "asked_questions": asked_questions,
        "answered_questions": answered_questions,
    })

logger = logging.getLogger(__name__)

@csrf_exempt
def delete_question(request, qus_id):
    """Deletes a question and all related answers."""
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        question = get_object_or_404(Question, qus_id=qus_id, user=request.user)

        with transaction.atomic():
            Answer.objects.filter(qus_id=qus_id).delete()
            question.delete()

        return JsonResponse({"message": "Question and its answers deleted"}, status=200)
    
    except Exception as e:
        logger.error(f"Failed to delete question: {str(e)}")
        return JsonResponse({"error": f"Failed to delete question: {str(e)}"}, status=400)

@csrf_exempt
def delete_answer(request, ans_id):
    """Deletes a single answer."""
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        answer = get_object_or_404(Answer, ans_id=ans_id, user=request.user)
        answer.delete()
        return JsonResponse({"message": "Answer deleted"}, status=200)

    except Exception as e:
        logger.error(f"Failed to delete answer: {str(e)}")
        return JsonResponse({"error": f"Failed to delete answer: {str(e)}"}, status=400)


@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('accounts:login')   

