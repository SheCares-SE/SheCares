from django.urls import path
from .views import patient_dashboard ,book_appointment, patient_appointments

app_name = 'patient'  # ✅ Define the app namespace

urlpatterns = [
    path('dashboard/', patient_dashboard, name='patient_dashboard'),  # ✅ Now we use 'patients:patient_dashboard'
    path('book_appointment/', book_appointment, name='book_appointment'),
    path('appointments/', patient_appointments, name='patient_appointments'),
    # path('recommend/', recommend_doctor, name='recommend_doctor'),
    # path("get_doctors/", get_doctors, name="get_doctors"),
]