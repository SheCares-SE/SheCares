from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RoleSelectionForm, DoctorSignupForm, PatientSignupForm
from .models import User, PatientProfile, DoctorProfile
from gync.models import Appointment
from gync.models import Doctor  # Fetch doctor data
from patient.models import Patient  # Fetch patient data

def edit_patient_profile(request):
    """Handle editing of a patient's profile"""

    profile, created = PatientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PatientSignupForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = PatientSignupForm(instance=profile)

    return render(request, 'accounts/edit_patient_profile.html', {'form': form})


def select_role_view(request):
    """Step 1: Ask for the role"""
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            return redirect('signup_step2', role=role)
    else:
        form = RoleSelectionForm()
    return render(request, 'accounts/select_role.html', {'form': form})

#priyanka
def recommend_doctor_view(request):
    """Fetch specializations and doctors based on selection"""
    # Get distinct specializations from the database
    specializations = DoctorProfile.objects.values_list('specialization', flat=True).distinct()

    # Get selected specialization from user input
    selected_specialization = request.GET.get('specialization', '')

    # Fetch doctors based on the selected specialization
    doctors = DoctorProfile.objects.filter(specialization=selected_specialization) if selected_specialization else []

    return render(request, 'accounts/recommend_doctor.html', {
        'specializations': specializations,
        'doctors': doctors,
        'selected_specialization': selected_specialization
    })


def signup_view(request, role):
    """Step 2: Show appropriate signup form based on role"""
    if role not in ['doctor', 'patient']:
        return redirect('select_role')

    if request.method == 'POST':
        if role == 'doctor':
            form = DoctorSignupForm(request.POST)
        else:
            form = PatientSignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = role
            user.save()

            if role == 'doctor':
                DoctorProfile.objects.create(user=user, registration_number=form.cleaned_data['registration_number'],specialization=form.cleaned_data['specialization'])
            else:
                PatientProfile.objects.create(user=user, age=form.cleaned_data['age'])

            login(request, user)

            # Redirect based on role
            if role == 'doctor':
                return redirect('gync:doctor_dashboard')  
            else:
                return redirect('patient:patient_dashboard')  

    else:
        form = DoctorSignupForm() if role == 'doctor' else PatientSignupForm()

    return render(request, 'accounts/signup.html', {'form': form, 'role': role})


def profile_view(request):
    """Display the user's profile"""
def profile_view(request):
    user = request.user  # Get the currently logged-in user
    
    # Fetch the profile data based on the user's role
    if user.role == 'doctor':
        try:
            profile = Doctor.objects.get(user=user)  # Fetch data from the doctor table
        except Doctor.DoesNotExist:
            return render(request, 'profile_error.html', {'message': 'Doctor profile not found.'})
    elif user.role == 'patient':
        try:
            profile = Patient.objects.get(user=user)  # Fetch data from the patient table
        except Patient.DoesNotExist:
            return render(request, 'profile_error.html', {'message': 'Patient profile not found.'})
    
    # Return the profile page with user and profile data
    return render(request, 'accounts/profile.html', {'user': user, 'profile': profile})

def edit_doctor_profile(request):
    # Edit doctor's profile
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST, request.FILES, instance=request.user.doctorprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form =DoctorSignupForm(instance=request.user.doctorprofile)
    return render(request, 'edit_doctor_profile.html', {'form': form})

