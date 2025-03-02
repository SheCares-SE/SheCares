from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import connection
from gync.models import DoctorProfile
from SC.shared_models import Blog
from .forms import BlogForm
from django.http import JsonResponse
from accounts.models import User  
from django.http import HttpResponse
from .models import DoctorFeedback
from django.db.models import Avg
from .models import DoctorFeedback
from accounts.models import User
from django.shortcuts import render, get_object_or_404


# @login_required
# def gynecologist_profile_view(request, doctor_id):
#     doctor = get_object_or_404(DoctorProfile, user__id=doctor_id)
    
#     # Fetch feedbacks and calculate average rating
#     feedbacks = DoctorFeedback.objects.filter(doctor=doctor.user)
#     avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg']
    
#     if request.method == "POST":
#         form = FeedbackForm(request.POST)
#         if form.is_valid():
#             feedback = form.save(commit=False)
#             feedback.patient = request.user
#             feedback.doctor = doctor.user
#             feedback.save()
#             return redirect('gync:gynecologist_profile', doctor_id=doctor_id)  # Reload the page after submission
#     else:
#         form = FeedbackForm()
    
#     context = {
#         'doctor': doctor,
#         'feedbacks': feedbacks,
#         'avg_rating': avg_rating if avg_rating else "No ratings yet",
#         'form': form
#     }
#     return render(request, 'gync/gynecologist_profile.html', context)
# @login_required
# def gynecologist_profile_view(request, doctor_id):
#     # Fetch the doctor's profile using the doctor_id
#     doctor = get_object_or_404(DoctorProfile, user__id=doctor_id)
    
#     # Fetch all feedbacks for this doctor and calculate the average rating
#     feedbacks = DoctorFeedback.objects.filter(doctor=doctor.user)
#     avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg']
    
#     # Handle feedback submission
#     if request.method == "POST":
#         form = FeedbackForm(request.POST)
#         if form.is_valid():
#             feedback = form.save(commit=False)
#             feedback.patient = request.user  # The logged-in user (patient)
#             feedback.doctor = doctor.user   # The doctor being rated
#             feedback.save()
#             return redirect('gync:gynecologist_profile', doctor_id=doctor_id)  # Reload the page
#     else:
#         form = FeedbackForm()
    
#     # Prepare context for the template
#     context = {
#         'doctor': doctor,
#         'feedbacks': feedbacks,  # List of feedbacks to display
#         'avg_rating': round(avg_rating, 1) if avg_rating else "No ratings yet",  # Round the average rating for display
#         'form': form,  # Feedback form for the patient to submit
#     }
#     return render(request, 'gync/gynecologist_profile.html', context)

@login_required
def doctor_dashboard(request):
    return render(request, 'gync/doctor_dashboard.html')

def get_doctor_table_view(request, doctor_id):
    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
        return render(request, 'doctor_table.html', {'doctor': doctor})
    except DoctorProfile.DoesNotExist:
        return render(request, '404.html')  # Or any other error page

@login_required
def blog_list(request):
    blogs = Blog.objects.filter(author=request.user)
    show_all = request.GET.get("show_all", "false") == "true"
    blogs = Blog.objects.all() if show_all else blogs
    return render(request, "gync/blog_list.html", {"blogs": blogs, "show_all": show_all})


@login_required
def blog_create(request):
    if request.method == "POST":
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('gync:blog_list')
    else:
        form = BlogForm()
    return render(request, 'gync/blog_create.html', {'form': form})

@login_required
def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'gync/blog_detail.html', {'blog': blog})

#aishna


@login_required
def doctor_appointments_view(request):
    user_id = request.user.id


    # Fetch doctor ID from doctor_table
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM doctor_table WHERE user_id = %s", [user_id])
        doctor_table = cursor.fetchone()

    # if not doctor_table:
    #     return render(request, 'error_page.html', {'message': 'Doctor profile not found'})

    doctor_id = doctor_table[0]
    print(doctor_id)

    # Fetch Pending Appointments
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, p.username AS patient_name, p.email, a.status
            FROM gync_appointment a
            JOIN accounts_user p ON a.patient_id = p.id
            WHERE a.doctor_id = %s AND a.status = 'Pending'
            ORDER BY a.date DESC, a.time DESC;
        """, [doctor_id])
        pending_appointments = cursor.fetchall()

    print("Pending Appointments: ", pending_appointments)

    # Fetch Confirmed Appointments
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, p.username AS patient_name, p.email, a.status
            FROM gync_appointment a
            JOIN accounts_user p ON a.patient_id = p.id
            WHERE a.doctor_id = %s AND a.status = 'Confirmed'
            ORDER BY a.date DESC, a.time DESC;
        """, [doctor_id])
        confirmed_appointments = cursor.fetchall()

    print("Confirmed Appointments: ", confirmed_appointments)

    return render(request, 'gync/doctor_appointments.html', {
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments
    })

@login_required
def confirm_appointment(request, appointment_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE gync_appointment 
            SET status = 'Confirmed' 
            WHERE id = %s
        """, [appointment_id])
        connection.commit()

    return redirect('gync:doctor_appointments')

@login_required
def reject_appointment(request, appointment_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE gync_appointment 
            SET status = 'Rejected' 
            WHERE id = %s
        """, [appointment_id])
        connection.commit()

    return redirect('gync:doctor_appointments')