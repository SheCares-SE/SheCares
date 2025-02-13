from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from gync.models import Appointment, Availability
from gync.forms import AppointmentRequestForm

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'Pending'
            appointment.save()
            return redirect('/appointments/')
    else:
        form = AppointmentRequestForm()
    
    return render(request, 'patient/book_appointment.html', {'form': form})

@login_required
def patient_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'patient/patient_appointments.html', {'appointments': appointments})
@login_required
def patient_dashboard(request):
    return render(request, 'patient_dashboard.html')
