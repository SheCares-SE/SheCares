from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from .models import Availability, Appointment
from .forms import AvailabilityForm

@login_required
def doctor_dashboard(request):
    return render(request, 'doctor_dashboard.html')

@login_required
def update_availability(request):
    if request.method == "POST":
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            doctor = request.user.doctor_profile  # Ensure related_name in DoctorProfile
            doctor.availability = form.cleaned_data["availability"]
            doctor.save()
            return redirect("doctor_dashboard")
    else:
        form = AvailabilityForm()

    return render(request, "gync/update_availability.html", {"form": form})

@login_required
def doctor_appointments(request):
    appointments = Appointment.objects.filter(doctor=request.user)
    return render(request, 'gync/doctor_appointments.html', {'appointments': appointments})

@login_required
def confirm_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id, doctor=request.user)
    appointment.status = 'Confirmed'
    appointment.save()
    return redirect('doctor_appointments')

@login_required
def reject_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id, doctor=request.user)
    appointment.status = 'Rejected'
    appointment.save()
    return redirect('doctor_appointments')