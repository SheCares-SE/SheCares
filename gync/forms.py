from django import forms
from .models import Availability, Appointment
from SC.shared_models import Blog

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['date', 'start_time', 'end_time']

class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time']
        
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content']
