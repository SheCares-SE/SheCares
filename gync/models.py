from django.db import models
from django.contrib.auth import get_user_model
from SC.shared_models import Blog 

User = get_user_model()

class Symptom(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# class Doctor(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
#     registration_number = models.CharField(max_length=255, default="Unknown")  # Default value added
#     specialization = models.CharField(max_length=255, default="General")  # Default value added

#     def __str__(self):
#         return f"{self.user.username} - {self.specialization}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile_extra")
    registration_no = models.CharField(max_length=255, default="Unknown")  # Default value added
    specialization = models.CharField(max_length=255, default="General")  # Default value added
    profile_picture = models.ImageField(upload_to="doctor_pics/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"

class GyncProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

#Aishna
class Appointment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Rejected", "Rejected"),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_as_patient")
    doctor = models.ForeignKey(GyncProfile, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")

    class Meta:
        db_table = "gync_appointment"

    def __str__(self):
        return f"Appointment with {self.doctor.user.username} on {self.date} at {self.time} - {self.status}"