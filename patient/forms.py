# from django import forms
# from .models import Symptom

# class SymptomForm(forms.Form):
#     symptom = forms.ModelChoiceField(
#         queryset=Symptom.objects.all(),
#         empty_label="Select a Symptom",
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )



from django import forms
from accounts.models import DoctorProfile
from patient.models import Doctor  # Ensure you import the Doctor model
from django.db import connection  # To execute raw SQL queries
from .models import Appointments  # Assuming your model name is Appointment
from django import forms
from gync.models import Appointment, DoctorProfile

def get_doctor_choices():
    """Fetch doctors from accounts_user table."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username FROM accounts_user WHERE role = 'doctor'")  # Adjust column names if needed
        doctors = cursor.fetchall()
    return [(doctor[0], doctor[1]) for doctor in doctors]  # Returning (id, name) tuples

class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'status']  # Make sure these fields match the Appointment model

