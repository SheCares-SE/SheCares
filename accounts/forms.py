from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PatientProfile, DoctorProfile

class RoleSelectionForm(forms.Form):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
#modification done for SPECIALIZATION by priyanka
class DoctorSignupForm(UserCreationForm):
   
    registration_number = forms.CharField(max_length=50)
    specialization = forms.CharField(max_length=100)  # Added Specialization
    age = forms.IntegerField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','registration_number', 'specialization','age']

class PatientSignupForm(UserCreationForm):
    age = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','age']

#Aesha
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']