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
#modification done for SPECIALIZATION by priyanka
class DoctorSignupForm(UserCreationForm):
   
    registration_number = forms.CharField(max_length=50)
    specialization = forms.CharField(max_length=100)  # Added Specialization
    age = forms.IntegerField(required=True)
    city = forms.CharField(max_length=100, required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','registration_number', 'specialization','age','city']

class PatientSignupForm(UserCreationForm):
    age = forms.IntegerField(required=True)
    # city = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','age']

#Aesha
class ProfileUpdateForm(forms.ModelForm):
    registration_number = forms.CharField(required=False, label="Registration Number")
    specialization = forms.CharField(required=False, label="Specialization")
    username = forms.CharField(required=False, label="Username")
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
                username=self.cleaned_data.get('username')
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