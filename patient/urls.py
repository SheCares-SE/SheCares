from django.urls import path
from .views import patient_dashboard, cancel_appointment
from . import views

app_name = 'patient'  # Define the app namespace

urlpatterns = [
    path('dashboard/', patient_dashboard, name='patient_dashboard'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.patient_appointments, name='patient_appointments'),
    path('appointments/cancel/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
]
