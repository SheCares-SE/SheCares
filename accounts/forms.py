from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PatientProfile, DoctorProfile

class RoleSelectionForm(forms.Form):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

class DoctorSignupForm(UserCreationForm):
    registration_number = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PatientSignupForm(UserCreationForm):
    age = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']