from django.urls import path
from . import views

app_name = 'patient'  # Define the app namespace

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book_appointment/', views.book_appointment_search, name='book_appointment'),
    path('appointments/', views.patient_appointments, name='patient_appointments'),
    path('appointments/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    # path('book-doctor/<int:doctor_id>/', views.book_this_doctor, name='book_this_doctor'),
    # path('book-appointment/', views.book_appointment_search, name='book_appointment_search'),
    path('book-appointment/select/<int:doctor_id>/', views.select_doctor, name='select_doctor'),
    path('book-appointment/form/', views.book_appointment_form, name='book_appointment_form'),
]
