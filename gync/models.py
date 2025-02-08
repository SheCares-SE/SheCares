from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

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
