from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RoleSelectionForm, DoctorSignupForm, PatientSignupForm
from .models import User, PatientProfile, DoctorProfile

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
                DoctorProfile.objects.create(user=user, registration_number=form.cleaned_data['registration_number'])
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
