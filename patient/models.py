from django.db import models
from accounts.models import User, DoctorProfile
from accounts.models import PatientProfile  # Adjust the import path accordingly
  # If PatientProfile is in the same app

# patient/models.py

from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email= models.EmailField( max_length=254)
    # Add other fields as needed

    def __str__(self):
        return self.name


# Symptom Model
class Symptom(models.Model):
    name = models.CharField(max_length=255)
    related_specialization = models.CharField(max_length=100, default="General", null=True, blank=True)

    def __str__(self):
        return self.name

# Appointment Model
class Appointments(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending")

    class Meta:
        db_table = "appointment_table"

    def __str__(self):
        return f"Appointment on {self.appointment_date} at {self.appointment_time} - {self.patient.user.username} with Dr. {self.doctor.user.username}"
# In patient/models.py
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    # Other fields as needed
