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

# class AppointmentForm(forms.ModelForm):
#     doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), label="Select Doctor")
#     date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
from django import forms
from .models import Appointments, Doctor

from django import forms

class AppointmentForm(forms.Form):
    doctor = forms.ChoiceField(choices=[], label="Doctor", required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    def __init__(self, *args, **kwargs):
        doctors = kwargs.pop('doctors', [])  # Get doctors list from kwargs
        super().__init__(*args, **kwargs)
        self.fields['doctor'].choices = [(doc['id'], doc['username']) for doc in doctors]  # Populate dropdown


# class AppointmentForm(forms.ModelForm):
#     doctor = forms.ModelChoiceField(
#         queryset=Doctor.objects.all(),
#         widget=forms.Select(attrs={'id': 'doctor', 'class': 'form-select'})
#     )
#     date = forms.DateField(
#         widget=forms.DateInput(attrs={'type': 'date', 'id': 'id_date'})
#     )
#     time = forms.TimeField(
#         widget=forms.TimeInput(attrs={'type': 'time', 'id': 'id_time'})
#     )
    
#     class Meta:
#         model = Appointment
#         fields = ['doctor', 'date', 'time']

