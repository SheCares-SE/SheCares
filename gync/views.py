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
    print(f"Debug: Logged-in User ID -> {request.user.id}")
    print(f"Debug: Logged-in User Username -> {request.user.username}")

    user_id = request.user.id
    print(f"User ID: {user_id}")

    # Fetch doctor ID from doctor_table
    # with connection.cursor() as cursor:
    #     cursor.execute("SELECT id FROM doctor_table WHERE user_id = %s", [user_id])
    #     doctor_table = cursor.fetchone()
    with connection.cursor() as cursor:
          cursor.execute("SELECT id FROM doctor_table WHERE user_id = %s", [user_id])
          doctor_table = cursor.fetchone()
    print(f"Raw doctor_table result: {doctor_table}")  # Debugging line
    # if not doctor_table:  # Ensure doctor exists
    #     return render(request, 'error_page.html', {'message': 'Doctor profile not found'})

    doctor_id = doctor_table[0]
    print(f"Doctor ID: {doctor_id}")

    # Fetch Pending Appointments
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, p.username, p.email, a.status
            FROM gync_appointment a
            JOIN accounts_user p ON a.patient_id = p.id
            WHERE a.doctor_id = %s AND a.status = 'Pending'
            ORDER BY a.date DESC, a.time DESC;
        """, [doctor_id])
        pending_appointments = cursor.fetchall()

    # Fetch Confirmed Appointments
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, p.username, p.email, a.status
            FROM gync_appointment a
            JOIN accounts_user p ON a.patient_id = p.id
            WHERE a.doctor_id = %s AND a.status = 'Confirmed'
            ORDER BY a.date DESC, a.time DESC;
        """, [doctor_id])
        confirmed_appointments = cursor.fetchall()

    print("Pending Appointments:", pending_appointments)
    print("Confirmed Appointments:",confirmed_appointments)

    return render(request, 'gync/doctor_appointments.html', {
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments
    })

@login_required
def confirm_appointment(request, appointment_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE gync_appointment SET status = 'Confirmed' WHERE id = %s", [appointment_id])
        connection.commit()
    return redirect('gync:doctor_appointments')

@login_required
def reject_appointment(request, appointment_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE gync_appointment SET status = 'Rejected' WHERE id = %s", [appointment_id])
        connection.commit()
    return redirect('gync:doctor_appointments')
