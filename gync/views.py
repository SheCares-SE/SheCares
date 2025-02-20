from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from .models import Availability, Appointment
from .forms import AvailabilityForm
from gync.models import DoctorProfile
from SC.shared_models import Blog
from .forms import BlogForm
from django.shortcuts import get_object_or_404


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

# @login_required
# def doctor_appointments(request):
#     appointments = Appointment.objects.filter(doctor=request.user)
#     return render(request, 'gync/doctor_appointments.html', {'appointments': appointments})

@login_required
def doctor_appointments(request):
    # ✅ Get the doctor profile from the logged-in user
    doctor = Doctor.objects.get(user=request.user)  

    # ✅ Filter appointments where this doctor is assigned
    appointments = Appointment.objects.filter(doctor=doctor)  

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


def get_doctor_profile_view(request, doctor_id):
    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
        return render(request, 'doctor_profile.html', {'doctor': doctor})
    except DoctorProfile.DoesNotExist:
        return render(request, '404.html') # Or any other error page
    

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
            return redirect('blog_list')
    else:
        form = BlogForm()
    return render(request, 'gync/blog_create.html', {'form': form})

@login_required
def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'gync/blog_detail.html', {'blog': blog})