from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import connection
from gync.models import DoctorProfile
from SC.shared_models import Blog
from .forms import BlogForm
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from accounts.models import User, DoctorProfile

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
    # Get the "show_all" parameter from the URL query string
    show_all = request.GET.get("show_all", "false") == "true"

    if show_all:
        # If "show_all" is True, fetch all blogs
        blogs = Blog.objects.all()
    else:
        # If "show_all" is False, show only the blogs created by the current user (doctor)
        if request.user.role == 'doctor':
            blogs = Blog.objects.filter(author=request.user)
        else:
            blogs = Blog.objects.all()  # Non-doctor users can view all blogs (or you can customize this further)

    return render(request, 'gync/blog_list.html', {'blogs': blogs, 'show_all': show_all})

@login_required
def blog_create(request):
    if request.user.role != 'doctor':
        messages.error(request, "Only doctors can create blogs.")
        return redirect('gync:blog_list')

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

@login_required
def doctor_appointments_view(request):
    print(f"Debug: Logged-in User ID -> {request.user.id}")
    print(f"Debug: Logged-in User Username -> {request.user.username}")

    user_id = request.user.id
    print(f"User ID: {user_id}")

    with connection.cursor() as cursor:
          cursor.execute("SELECT id FROM doctor_table WHERE user_id = %s", [user_id])
          doctor_table = cursor.fetchone()
    print(f"Raw doctor_table result: {doctor_table}")  # Debugging line

    doctor_id = doctor_table[0]
    print(f"Doctor ID: {doctor_id}")

    # Fetch Pending Appointments
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, p.username, p.email, a.status
            FROM gync_appointment a
            JOIN accounts_user p ON a.patient_id = p.id
            WHERE a.doctor_id = (%s) AND a.status = 'Pending'
            ORDER BY a.date DESC, a.time DESC;
        """, [user_id])
        pending_appointments = cursor.fetchall()

    # Fetch Confirmed Appointments
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, p.username, p.email, a.status
            FROM gync_appointment a
            JOIN accounts_user p ON a.patient_id = p.id
            WHERE a.doctor_id = (%s) AND a.status = 'Confirmed'
            ORDER BY a.date DESC, a.time DESC;
        """, [user_id])
        confirmed_appointments = cursor.fetchall()

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



def get_available_slots(doctor_id, date=None):
    if date is None:
        date = timezone.localdate()

    # Fetch doctor profile details using the doctor_id
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT opening_time, closing_time, break_start, break_end 
            FROM doctor_table 
            WHERE user_id = %s
        """, [doctor_id])  # Use doctor_id directly
        row = cursor.fetchone()
    
    if not row:
        return []
    
    opening_time, closing_time, break_start, break_end = row
    
    if not opening_time or not closing_time:
        return []
    
    opening_time = timezone.make_aware(datetime.combine(date, opening_time))
    closing_time = timezone.make_aware(datetime.combine(date, closing_time))
    
    if break_start and break_end:
        break_start = timezone.make_aware(datetime.combine(date, break_start))
        break_end = timezone.make_aware(datetime.combine(date, break_end))
    
    # Fetch confirmed appointments for the doctor on the given date
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT time 
            FROM gync_appointment 
            WHERE doctor_id = %s AND status = 'Confirmed' AND date = %s
        """, [doctor_id, date])  # Use doctor_id directly
        appointments = cursor.fetchall()
    
    booked_slots = set()
    for appt in appointments:
        start_time = timezone.make_aware(datetime.combine(date, appt[0]))
        end_time = start_time + timedelta(minutes=30)
        booked_slots.add((start_time, end_time))
    
    available_slots = []
    
    def generate_slots(start, end):
        current_time = start
        slot_start = None

        while current_time + timedelta(minutes=30) <= end:
            slot_end = current_time + timedelta(minutes=30)
            
            if any(bs[0] < slot_end and bs[1] > current_time for bs in booked_slots):
                if slot_start:
                    available_slots.append((
                        slot_start.strftime("%I:%M %p").lstrip("0"),
                        current_time.strftime("%I:%M %p").lstrip("0")
                    ))
                    slot_start = None
            else:
                if not slot_start:
                    slot_start = current_time
            
            current_time += timedelta(minutes=30)
        
        if slot_start:
            available_slots.append((
                slot_start.strftime("%I:%M %p").lstrip("0"),
                end.strftime("%I:%M %p").lstrip("0")
            ))
    
    if break_start and break_end:
        generate_slots(opening_time, break_start)
        generate_slots(break_end, closing_time)
    else:
        generate_slots(opening_time, closing_time)
    
    return available_slots

@login_required
def doctor_available_slots(request, doctor_id):
    date_str = request.GET.get('date')
    date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.localdate()
    
    # Fetch the doctor object to pass to the template
    doctor = get_object_or_404(User, id=doctor_id)
    
    # Pass the doctor_id (integer) to the get_available_slots function
    available_slots = get_available_slots(doctor_id, date)
    
    return render(request, 'gync/doctor_available_slots.html', {
        'available_slots': available_slots,
        'doctor': doctor,
        'date': date
    })