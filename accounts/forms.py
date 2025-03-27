from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PatientProfile, DoctorProfile
from accounts.models import User


class RoleSelectionForm(forms.Form):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)


class DoctorSignupForm(UserCreationForm):
    registration_number = forms.CharField(max_length=50)
    specialization = forms.CharField(max_length=100) 
    age = forms.IntegerField(required=True)
    city = forms.CharField(max_length=100, required=True)
  
    OPENING_TIME = [
        ('07:00', '07:00 AM'), ('07:30', '07:30 AM'), ('08:00', '08:00 AM'), ('08:30', '08:30 AM'),
        ('09:00', '09:00 AM'), ('09:30', '09:30 AM'), ('10:00', '10:00 AM'), ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'), ('11:30', '11:30 AM')
    ]
    CLOSING_TIME = [
        ('20:00', '08:00 PM'), ('20:30', '08:30 PM'),
        ('21:00', '09:00 PM'), ('21:30', '09:30 PM'), ('22:00', '10:00 PM'), ('22:30', '10:30 PM'),
        ('23:00', '11:00 PM')
    ]    
    BREAK_START = [
        ('12:00', '12:00 PM'), ('12:30', '12:30 PM'), ('13:00', '01:00 PM'), ('13:30', '01:30 PM'),
        ('14:00', '02:00 PM')
    ]
    BREAK_END = [
        ('14:00', '02:00 PM'), ('14:30', '02:30 PM'), ('15:00', '03:00 PM'), ('15:30', '03:30 PM'),
        ('16:00', '04:00 PM'), ('16:30', '04:30 PM'), ('17:00', '05:00 PM')
    ]
    opening_time = forms.ChoiceField(choices=OPENING_TIME, required=True)
    closing_time = forms.ChoiceField(choices=CLOSING_TIME, required=True)
    break_start = forms.ChoiceField(choices=BREAK_START, required=True)
    break_end = forms.ChoiceField(choices=BREAK_END, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'registration_number', 'specialization', 'age', 'city', 'opening_time', 'closing_time', 'break_start', 'break_end']


class PatientSignupForm(UserCreationForm):
    age = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','age']


class ProfileUpdateForm(forms.ModelForm):
    registration_number = forms.CharField(required=False, label="Registration Number")
    specialization = forms.CharField(required=False, label="Specialization")
    username = forms.CharField(required=False, label="Username")
    city = forms.CharField(required=False, label="City")
    opening_time = forms.TimeField(required=False, label="Opening Time")
    closing_time = forms.TimeField(required=False, label="Closing Time")
    break_start = forms.TimeField(required=False, label="Break Start")
    break_end = forms.TimeField(required=False, label="Break End")
    age = forms.IntegerField(required=False, label="Age")
    profile_picture = forms.ImageField(required=False, label="Profile Picture")

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super().__init__(*args, **kwargs)

        if user_type == 'doctor':
            self.fields.pop('age')  # Remove age for doctors
        elif user_type == 'patient':
            self.fields.pop('registration_number')
            self.fields.pop('specialization')  # Remove doctor-specific fields
            self.fields.pop('city') 
            self.fields.pop('opening_time')
            self.fields.pop('closing_time')
            self.fields.pop('break_start')
            self.fields.pop('break_end')    
     

    class Meta:
        model =User
        fields = ['profile_picture']  # Only profile picture is in accounts_user

    def save(self, user, commit=True):
        """Custom save method to update the correct table."""
        instance = super().save(commit=False)

        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data.get('profile_picture')
            user.save(update_fields=['profile_picture'])  # Update only profile picture

        if hasattr(user, 'doctortable'):  # If the user is a doctor
            from gync.models import doctor_table  # Importing to avoid circular imports
            doctor_table.objects.filter(doctor_id=user.id).update(
                registration_number=self.cleaned_data.get('registration_number'),
                specialization=self.cleaned_data.get('specialization'),
                username=self.cleaned_data.get('username'),
                city=self.cleaned_data.get('city'),
                opening_time=self.cleaned_data.get('opening_time'),
                closing_time=self.cleaned_data.get('closing_time'),
                break_start=self.cleaned_data.get('break_start'),
                break_end=self.cleaned_data.get('break_end')
            )

        elif user.role == 'patient':  # If the user is a patient
            from patient.models import patient_table  # Importing to avoid circular imports
            patient_table.objects.filter(userid=user.id).update(
                age=self.cleaned_data.get('age'),
                username=self.cleaned_data.get('username')
            )

        if commit:
            instance.save()
        return instance
   
#Aesha
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']