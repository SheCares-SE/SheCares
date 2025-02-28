from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import connection
from gync.models import DoctorProfile
from SC.shared_models import Blog
from .forms import BlogForm

from django.http import HttpResponse

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
    return render(request, 'gync/blog_list.html', {'blogs': blogs})

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
    # Get the user ID
    user_id = request.user.id
    
    # Retrieve the doctor profile ID using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM doctor_table WHERE user_id = %s", [user_id])
        doctor_table = cursor.fetchone()

    # If no doctor profile exists, you may want to show an error message or redirect
    # if not doctor_table:
    #     # Redirect to a different page, or show an error message
    #     return render(request, 'error_page.html', {'message': 'Doctor profile not found'})

    # Assuming `doctor_table` exists, fetch the doctor ID
    doctor_id = doctor_table[0]  # Accessing the first element (ID) from the tuple

    # Retrieve pending appointments for the doctor
    with connection.cursor() as cursor:
        # Fetch the doctor details (ID should already be in doctor_table)
        cursor.execute("""
            SELECT a.id, a.date, a.time, a.status, p.username 
            FROM gync_appointment a
            JOIN accounts_user p ON a.patient_id = p.id 
            WHERE a.doctor_id = %s AND a.status = 'Pending'
        """, [doctor_id])

        appointments = cursor.fetchall()

    # Render the appointments in the template
    return render(request, 'gync/doctor_appointments.html', {'appointments': appointments})

@login_required
def confirm_appointment(request, appointment_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE gync_appointment
            SET status = 'Confirmed'
            WHERE id = %s
        """, [appointment_id])
    return redirect('gync:doctor_appointments')

@login_required
def reject_appointment(request, appointment_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE gync_appointment
            SET status = 'Rejected'
            WHERE id = %s
        """, [appointment_id])
    return redirect('gync:doctor_appointments')
