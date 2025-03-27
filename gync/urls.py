from django.urls import path
from .views import doctor_dashboard, blog_list, blog_create, blog_detail ,doctor_available_slots
from .import views

app_name = 'gync'  # Define the app namespace

urlpatterns = [
    path('appointments/', views.doctor_appointments_view, name='doctor_appointments'),
    path('appointments/confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('appointments/reject/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('blogs/', blog_list, name='blog_list'),
    path('blogs/create/', blog_create, name='blog_create'),
    path('blogs/<int:blog_id>/', blog_detail, name='blog_detail'),
    path('doctor/<int:doctor_id>/available-slots/', views.doctor_available_slots, name='doctor_available_slots'),
]
