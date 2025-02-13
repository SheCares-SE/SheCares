from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="patient")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Profile picture field

    def __str__(self):
        return self.username

# Patient Profile Model
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accounts_patient_profile')  # Unique related_name
    age = models.PositiveIntegerField(default=30)  # Default age value
    is_private = models.BooleanField(default=False)  # Privacy setting

    class Meta:
        db_table = "accounts_patient_profile_table"  # Unique table name

    def __str__(self):
        return f"Patient Profile: {self.user.username}"

# Doctor Profile Model
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_user_profile')  # Unique related_name
    registration_number = models.CharField(max_length=20, default="Not Registered")  # Default value for registration number
    specialization = models.CharField(max_length=100, default="General")  # Default value for specialization

    class Meta:
        db_table = "doctor_table"  # Unique table name for DoctorProfile

    def __str__(self):
        return f"Doctor: {self.user.username} - {self.specialization}"

# Appointment Model
class Appointment(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='patient_appointments')  # Use unique related_name
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='doctor_appointments')  # Use unique related_name
    date = models.DateField(default="2025-01-01")  # Default date value (example)
    time = models.TimeField(default="09:00:00")  # Default time value (example)

    class Meta:
        db_table = "gync_appointment"  # Unique table name for Appointment (make sure only one model uses this table)

    def __str__(self):
        return f"Appointment on {self.date} at {self.time} - {self.patient.user.username} with Dr. {self.doctor.user.username}"
