from django.urls import path,include
from .views import signup_view, select_role_view, recommend_doctor_view
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy
from patient.views import patient_dashboard  
from gync.views import doctor_dashboard  
from . import views
from .views import signup_view, patient_appointments_view, doctor_requests_view, approve_request, reject_request
from .views import faq_page, add_question, add_answer

urlpatterns = [
    #path("gync/", include("gync.urls", namespace="gync")),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', views.login_view, name='login'),
    path('select-role/', select_role_view, name='select_role'),
    path('signup/<str:role>/', signup_view, name='signup_step2'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy("login")), name="logout"),
    path("patient-dashboard/", patient_dashboard, name="patient_dashboard"),
    path("doctor-dashboard/", doctor_dashboard, name="doctor_dashboard"),
     #priyanka
    path("recommend-doctor/", recommend_doctor_view, name="recommend_doctor"), 
     #Urvashi
    path("faq/", faq_page, name="faq_page"),
    path("faq/add_question/", add_question, name="add_question"),
    path("faq/add_answer/<int:question_id>/", add_answer, name="add_answer"),
    #Aishna
    path('patient/appointments/', patient_appointments_view, name='patient_appointments'),
    path('doctor/requests/', doctor_requests_view, name='doctor_requests'),
    path('doctor/requests/approve/<int:appointment_id>/', approve_request, name='approve_request'),
    path('doctor/requests/reject/<int:appointment_id>/', reject_request, name='reject_request'),

]