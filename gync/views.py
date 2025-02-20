from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from .models import Availability, Appointment
from .forms import AvailabilityForm
from gync.models import DoctorProfile
from django.shortcuts import  get_object_or_404
from gync.models import Appointment

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
    # Retrieve the DoctorProfile associated with the logged-in user
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    
    # Filter appointments using the doctor_profile
    appointments = Appointment.objects.filter(doctor=doctor_profile)

    return render(request, 'gync/doctor_appointments.html', {'appointments': appointments})


def get_doctor_profile_view(request, doctor_id):
    doctor_profile = get_object_or_404(DoctorProfile, id=doctor_id)
    return render(request, 'gync/doctor_profile.html', {'doctor_profile': doctor_profile})