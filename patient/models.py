from django.db import models
from  accounts.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_user_profile" , default="xyz")
    age = models.IntegerField(default=5)
    
    def __str__(self):
        return f"{self.user.username} - Age: {self.age}"
    
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile_details")
    age = models.IntegerField(default=5)
    profile_picture = models.ImageField(upload_to='patient_pics/', blank=True, null=True,default="xyz")
    
    class Meta:
        db_table = "patient_table"  
    def __str__(self):
        return f"{self.user.username} - {self.age}"

    
class Symptom(models.Model):
    name = models.CharField(max_length=255, default="xyz")
    related_specialization = models.CharField(max_length=100, default="General", null=True, blank=True)

    def __str__(self):
        return self.name

