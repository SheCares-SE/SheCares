from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES ,default="Patient")
    
# Patient Profile Model
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField()
    
    class Meta:
        db_table = "patient_table"  # Match with your MySQL table
    def __str__(self):
        return f"Patient: {self.user.username}"

# Doctor Profile Model
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    registration_number = models.CharField(max_length=20)

    class Meta:
        db_table = "doctor_table"  # Match with your MySQL table
    def __str__(self):
        return f"Doctor: {self.user.username}"