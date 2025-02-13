from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

class Symptom(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    registration_number = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"
    
# class DoctorProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     registration_no = models.CharField(max_length=255)
#     specialization = models.CharField(max_length=255)
#     profile_picture = models.ImageField(upload_to='doctor_pics/', blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.specialization}"
    

class Availability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor} - {self.date} ({self.start_time} - {self.end_time})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Appointment with {self.doctor} on {self.date} at {self.time} - {self.status}"
