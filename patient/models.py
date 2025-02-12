from django.db import models

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

