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


# class FeedbackForm(forms.ModelForm):
#     class Meta:
#         model = DoctorFeedback
#         fields = ['rating', 'feedback']  # Fields the patient can fill
#         widgets = {
#             'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),  # Assuming rating is 1-5
#             'feedback': forms.Textarea(attrs={'rows': 3}),
#         }