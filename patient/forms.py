from django import forms
from accounts.models import DoctorProfile
from patient.models import Doctor  # Ensure you import the Doctor model
from django.db import connection  # To execute raw SQL queries
from .models import Appointments  # Assuming your model name is Appointment
from gync.models import Appointment, DoctorProfile

def get_doctor_choices():
    """Fetch doctors from accounts_user table."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username FROM accounts_user WHERE role = 'doctor'")  # Adjust column names if needed
        doctors = cursor.fetchall()
    return [(doctor[0], doctor[1]) for doctor in doctors]  # Returning (id, name) tuples

class AppointmentForm(forms.Form):
    doctor = forms.ChoiceField(label='Select Doctor')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=True)

    def __init__(self, *args, **kwargs):
        doctors = kwargs.pop('doctors', [])
        super().__init__(*args, **kwargs)
        # Convert the dictionary format to choices
        self.fields['doctor'].choices = [(doc['id'], doc['username']) for doc in doctors]

