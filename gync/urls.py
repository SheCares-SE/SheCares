from django.urls import path
from .views import doctor_dashboard
from . import views
from .views import blog_list, blog_create, blog_detail 
from .views import gynecologist_profile_view

app_name = 'gync'  # Define the app namespace

urlpatterns = [
    # path('doctor/<int:doctor_id>/', views.gynecologist_profile_view, name='gynecologist_profile'),
    path('appointments/', views.doctor_appointments_view, name='doctor_appointments'),
    path('appointments/confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('appointments/reject/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('dashboard/', doctor_dashboard, name='doctor_dashboard'),
    # path('doctor/<int:doctor_id>/', views.get_doctor_table_view, name='doctor_table'),
    # path('update_availability/', update_availability, name='update_availability'),
    # path('appointments-doctor/', doctor_appointments, name='doctor_appointments'),
    path('blogs/', blog_list, name='blog_list'),
    path('blogs/create/', blog_create, name='blog_create'),
    path('blogs/<int:blog_id>/', blog_detail, name='blog_detail'),
]
