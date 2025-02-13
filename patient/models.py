from django.db import models
from  accounts.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    age = models.IntegerField()
    
    def __str__(self):
        return f"{self.user.username} - Age: {self.age}"
    
# class PatientProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
#     age = models.IntegerField()
#     profile_picture = models.ImageField(upload_to='patient_pics/', blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.age}"
# class Doctor(models.Model):
#     name = models.CharField(max_length=100)
#     specialization = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)

#     def __str__(self):
#         return self.name
    
# class Symptom(models.Model):
#     name = models.CharField(max_length=255)
#     related_specialization = models.CharField(
#         max_length=100, default="General", null=True, blank=True
#     )

#     def __str__(self):
#         return self.name

