from django.urls import path
from .views import signup_view, select_role_view, recommend_doctor_view
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy

# ✅ Import views correctly from their respective apps
from patient.views import patient_dashboard  
from gync.views import doctor_dashboard  

urlpatterns = [
    path('select-role/', select_role_view, name='select_role'),
    path('signup/<str:role>/', signup_view, name='signup_step2'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy("login")), name="logout"),
    path("patient/dashboard/", patient_dashboard, name="patient_dashboard"),
    path("doctor/dashboard/", doctor_dashboard, name="doctor_dashboard"),
     #priyanka
    path("recommend-doctor/", recommend_doctor_view, name="recommend_doctor"),  
]