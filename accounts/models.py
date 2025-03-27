from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="patient")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)    
    age = models.IntegerField(null=True, blank=True)  # Add age field
    
    def __str__(self):
        return self.username

# Patient Profile Model
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField(default=30)
    is_private = models.BooleanField(default=False)

    class Meta:
        db_table = "patient_table"

    def __str__(self):
        return f"{self.user.username}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_table', default=None)
    registration_number = models.CharField(max_length=20, default="Not Registered")
    specialization = models.CharField(max_length=100, default="General")
    account_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_account', to_field='id', null=True, blank=True)
    city = models.CharField(max_length=255, default="Default")
    opening_time = models.TimeField(null=True, blank=True)  
    closing_time = models.TimeField(null=True, blank=True)  
    break_start = models.TimeField(null=True, blank=True)  
    break_end = models.TimeField(null=True, blank=True)  # New field for break end

    class Meta:
        db_table = "doctor_table"

    def __str__(self):
        return f"Dr. {self.user.username} - {self.specialization}"



User = get_user_model()

class Question(models.Model):
    qus_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    upvote_count = models.IntegerField(default=0)  # New field for likes

    def __str__(self):
        return self.text

class Answer(models.Model):
    ans_id = models.AutoField(primary_key=True)
    qus = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    upvote_count = models.IntegerField(default=0)  # New field for likes

    def __str__(self):
        return self.text


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')
    

