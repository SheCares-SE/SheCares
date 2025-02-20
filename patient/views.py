from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from SC.shared_models import Blog
from django.db import connection
from gync.models import DoctorProfile, Appointment
from .forms import AppointmentForm
import logging
logger = logging.getLogger(__name__)

# Ensure no multiple definitions for patient_dashboard

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
        cursor.execute("SELECT id, username FROM accounts_user WHERE role = 'doctor'")
        doctors = cursor.fetchall()
    return [{"id": doctor[0], "username": doctor[1]} for doctor in doctors]  # Return list of dictionaries

@login_required
def book_appointment(request):
    doctors = get_doctors()  # Get all doctors
    if request.method == 'POST':
        form = AppointmentForm(request.POST)  # Initialize form with POST data

        if form.is_valid():
            appointment = form.save(commit=True)
            appointment.patient = request.user  # Set the logged-in user as the patient

            # Correctly format the date and time for the SQL query
            date = appointment.date.strftime('%Y-%m-%d')
            time = appointment.time.strftime('%H:%M:%S')
            status = appointment.status
            # Insert into the appointment table using raw SQL
            with connection.cursor() as cursor:
                try:
                    cursor.execute("""
                        INSERT INTO gync_appointment (patient_id, doctor_id, date, time, status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [appointment.patient.id, appointment.doctor.id, appointment.date, appointment.time, appointment.status])
                    logger.debug(f"Appointment booked: Patient ID: {appointment.patient.id}, Doctor ID: {appointment.doctor.id}, Date: {appointment.date}, Time: {appointment.time}")
                    return redirect('patient:patient_appointments')
                except Exception as e:
                    logger.error(f"Error booking appointment: {e}")
    else:
        form = AppointmentForm()  # Initialize empty form for GET request

    return render(request, 'patient/book_appointment.html', {'form': form, 'doctors': doctors})

@login_required
def patient_appointments(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.date, a.time, a.status, d.user_id
            FROM gync_appointment a
            JOIN gync_doctorprofile d ON a.doctor_id = d.id
            WHERE a.patient_id = %s
        """, [request.user.id])
        appointments = cursor.fetchall()
    return render(request, 'patient/patient_appointments.html', {'appointments': appointments})
