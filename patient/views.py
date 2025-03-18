from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from SC.shared_models import Blog
from django.db import connection
from gync.models import DoctorProfile, Appointment
from .forms import AppointmentForm
import logging
from django.http import JsonResponse
from .models import Doctor
from datetime import datetime , timedelta 


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
   

# @login_required
# def book_appointment(request):
#     doctors = get_doctors()  # Get all doctors

#     if request.method == 'POST':
        
#         form = AppointmentForm(request.POST)
        
#         print(form.is_valid())
#         if form.is_valid():
#             appointment = form.save(commit=False)  # Don't save yet
#             appointment.patient = request.user  # Assign logged-in user as patient
            
#             doctor_id = appointment.doctor.id
#             patient_id = request.user.id
#             date = appointment.date.strftime('%Y-%m-%d')
#             time = appointment.time.strftime('%H:%M:%S')
#             status = "Pending"  # Default status

#             # Insert into the database using raw SQL
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO gync_appointment (patient_id, doctor_id, date, time, status) 
#                     VALUES (%s, %s, %s, %s, %s)
#                 """, [patient_id, doctor_id, date, time, status])

#             return redirect('patient:patient_appointments')  # Redirect after successful booking

#     else:
#         form = AppointmentForm()  # Empty form for GET request

#     return render(request, 'patient/book_appointment.html', {'form': form, 'doctors': doctors})

def get_doctors():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username FROM accounts_user WHERE role = 'doctor'")
        doctors = cursor.fetchall()
    return [{"id": doctor[0], "username": doctor[1]} for doctor in doctors]  # Return list of dictionaries

@login_required
def book_appointment(request):
    doctors = get_doctors()  # Get doctors using raw SQL

    if request.method == 'POST':
        form = AppointmentForm(request.POST, doctors=doctors)
        print(form.is_valid())  # Pass doctors list
        if form.is_valid():
            doctor_id = form.cleaned_data['doctor']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            date_new=date.strftime('%Y-%m-%d')
            time_new= str(time.strftime('%H:%M:%S')) 
            patient_id = request.user.id 
            print(f"Selected Doctor ID: {doctor_id}")  # Debugging print
            # Save appointment using raw SQL query
            print(f"Appointment Date: {date_new}, Appointment Time: {time_new}")
            with connection.cursor() as cursor:
                query = """ INSERT INTO gync_appointment (patient_id, doctor_id, date, time, status) VALUES (%s, %s, %s, %s, 'Pending')"""
                params = (patient_id, doctor_id, str(date_new), str(time_new))

                print("Executing query:", query % params)  # Log the query with parameters
                cursor.execute(query, params)


            return redirect('patient:patient_appointments')
        else:
            print(form.errors)  # Debugging errors
    else:
        form = AppointmentForm(doctors=doctors)  # Pass doctors list to form

    return render(request, 'patient/book_appointment.html', {'form': form, 'doctors': doctors})
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
            print(f"Appointment {appointment_id} cancelled successfully")
        else:
            print("Cannot cancel appointment less than 1 hour before the time.")

    return redirect('patient:patient_appointments')