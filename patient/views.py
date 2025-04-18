from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from gync.models import DoctorProfile
from .forms import AppointmentForm
from django.http import Http404
import logging
from datetime import datetime , timedelta
from .models import DoctorProfile
from django.contrib import messages


logger = logging.getLogger(__name__)


@login_required
def patient_dashboard(request):
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, a.status, g.user_id, u.username, g.specialization
            FROM gync_appointment a
            JOIN gync_doctorprofile g ON a.doctor_id = g.id
            JOIN accounts_user u ON g.user_id = u.id
            WHERE a.patient_id = %s
        """, [request.user.id])
        appointments = cursor.fetchall()

    return render(request, 'patient/patient_dashboard.html', {
        'appointments': appointments,
    })



def get_doctors():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, username 
            FROM accounts_user 
            WHERE role = 'doctor'
        """)
        # Convert to list of dictionaries consistently
        return [{"id": doctor[0], "username": doctor[1]} for doctor in cursor.fetchall()]


@login_required
def book_appointment(request):
    search_query = request.GET.get('doctor_search', '')
    selected_doctor = None
    doctors = []

    # Handle doctor selection
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        if doctor_id:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username 
                    FROM accounts_user 
                    WHERE id = %s AND role = 'doctor'
                """, [doctor_id])
                doctor_data = cursor.fetchone()
                if doctor_data:
                    selected_doctor = {"id": doctor_data[0], "username": doctor_data[1]}

    # Handle doctor search
    if search_query:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username 
                FROM accounts_user
                WHERE username LIKE %s AND role = 'doctor'
            """, ['%' + search_query + '%'])
            doctors = [{"id": doctor[0], "username": doctor[1]} for doctor in cursor.fetchall()]

    form = AppointmentForm()

    return render(request, 'patient/book_appointment.html', {
        'form': form,
        'doctors': doctors,
        'search_query': search_query,
        'selected_doctor': selected_doctor,
    })


@login_required
def book_this_doctor(request, doctor_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, username 
                FROM accounts_user 
                WHERE id = %s AND role = 'doctor'
            """, [doctor_id])
            doctor = cursor.fetchone()
            
            if doctor:
                request.session['selected_doctor_id'] = doctor_id
                messages.success(request, f'Doctor selected: Dr. {doctor[1]}')
                return redirect('patient:book_appointment')
            
    messages.error(request, 'Invalid doctor selection')
    return redirect('patient:book_appointment')


# Function to validate appointment time
@login_required
def is_valid_appointment(doctor, appointment_time):
    """Check if the appointment time is within working hours and not during break."""
    opening = doctor.opening_time
    closing = doctor.closing_time
    break_start = doctor.break_start
    break_end = doctor.break_end

    if not (opening <= appointment_time <= closing):  # Must be within working hours
        return False
    if break_start <= appointment_time <= break_end:  # Must not be during break
        return False
    return True


@login_required
def patient_appointments(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, a.status, u.username
            FROM gync_appointment a
            JOIN accounts_user u ON a.doctor_id = u.id
            WHERE a.patient_id = %s
            ORDER BY a.date DESC, a.time DESC
        """, [request.user.id])
        
        appointments = cursor.fetchall()  # Fetch results

    # Convert to list of dictionaries for the template
    appointments_list = [
        {
            "id": row[0], 
            "date": row[1], 
            "time": row[2], 
            "status": row[3], 
            "doctor_username": row[4]
        }
        for row in appointments
    ]
    return render(request, "patient/patient_appointments.html", {"appointments": appointments_list})


@login_required
def cancel_appointment(request, appointment_id):
    """Allow patient to cancel their appointment if it's at least 1 hour away."""
    with connection.cursor() as cursor:
        # Fetch the appointment time
        cursor.execute("SELECT date, time FROM gync_appointment WHERE id = %s AND patient_id = %s", 
                       [appointment_id, request.user.id])
        appointment = cursor.fetchone()
        current_time = datetime.now()
        if not appointment:
            print("Invalid appointment or unauthorized access")
            return redirect('patient:patient_appointments')

        appointment_datetime = f"{appointment[0]} {appointment[1]}"  # Convert date + time
        appointment_time = datetime.strptime(appointment_datetime, "%Y-%m-%d %H:%M:%S")

        # Check if the appointment is at least 1 hour away
        if appointment_time > (current_time + timedelta(hours=1)):
            cursor.execute("UPDATE gync_appointment SET status = 'Cancelled' WHERE id = %s", [appointment_id])
            # print(f"Appointment {appointment_id} cancelled successfully")
        else:
            print("Cannot cancel appointment less than 1 hour before the time.")
    return redirect('patient:patient_appointments')