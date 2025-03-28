from django import forms
from SC.shared_models import Blog
from .models import Appointment
from .models import GyncProfile

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content']
#Aishna
class Appointment(forms.Form):
    doctor = forms.ModelChoiceField(queryset=GyncProfile.objects.all(), required=True, empty_label="Select Doctor")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time']

from django import forms
from .models import Appointment  # Adjust this import based on your actual model

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'doctor', 'patient', 'status']
