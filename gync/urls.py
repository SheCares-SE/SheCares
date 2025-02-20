from django.urls import path
from .views import doctor_dashboard
# from .views import update_availability, doctor_appointments, confirm_appointment, reject_appointment
from . import views

app_name = 'gync'  # ✅ Define the app namespace

urlpatterns = [
    
    path('dashboard/', doctor_dashboard, name='doctor_dashboard'),  # ✅ Now we use 'gynecologists:doctor_dashboard'
    path('doctor/<int:doctor_id>/', views.get_doctor_profile_view, name='doctor_profile'),
    # path('update_availability/', update_availability, name='update_availability'),
    # path('appointments-doctor/', doctor_appointments, name='doctor_appointments'),
    # path('confirm_appointment/<int:appointment_id>/', confirm_appointment, name='confirm_appointment'),
    # path('reject_appointment/<int:appointment_id>/', reject_appointment, name='reject_appointment'),
    
]
