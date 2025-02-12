from django.contrib.auth.models import AbstractUser
from django.db import models
# from accounts.models import CustomUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="patient")
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Profile picture field


# class Gynecologist(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
#     registration_no = models.CharField(max_length=100, unique=True)
#     specialization = models.CharField(max_length=255)

#     def __str__(self):
#         return self.user.first_name



# # Patient Profile Model
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField()
    is_private = models.BooleanField(default=False)  # Privacy setting


    class Meta:
        db_table = "patient_table"
    
    def __str__(self):
        return f"Patient: {self.user.username}"
    


#modification done for SPECIALIZATION by priyanka
# Doctor Profile Model
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    registration_number = models.CharField(max_length=20)
    specialization = models.CharField(max_length=100)
    class Meta:
        db_table = "doctor_table"
    
    def __str__(self):
        return f"Doctor: {self.user.username} - {self.specialization}"
    
# class Appointment(models.Model):
#     patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
#     doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
#     date = models.DateField()
#     time = models.TimeField()

#     class Meta:
#         db_table = "gync_appointment"

#     def __str__(self):
#         return f"Appointment on {self.date} at {self.time} - {self.patient.user.username} with Dr. {self.doctor.user.username}"
