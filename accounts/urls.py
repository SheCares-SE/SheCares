from django.urls import path,include
from .views import signup_view, select_role_view, recommend_doctor_view
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy
from .views import edit_patient_profile, profile_view, edit_doctor_profile
from . import views

# ✅ Import views correctly from their respective apps
from patient.views import patient_dashboard  
from gync.views import doctor_dashboard  

urlpatterns = [
    #  path('gync/', include('gync.urls')),
    path('login/', views.login_view, name='login'),
    path('profile/', profile_view, name='profile'),
    path('edit-doctor-profile/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('edit-patient-profile/', views.edit_patient_profile, name='edit_patient_profile'),
    path('select-role/', select_role_view, name='select_role'),
    path('signup/<str:role>/', signup_view, name='signup_step2'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy("login")), name="logout"),
    path("patient-dashboard/", patient_dashboard, name="patient_dashboard"),
    path("doctor-dashboard/", doctor_dashboard, name="doctor_dashboard"),
     #priyanka
    path("recommend-doctor/", recommend_doctor_view, name="recommend_doctor"),  
    
    
    # path('patient/profile/', patient_profile, name='patient_profile'),
    # path('gynecologist/profile/', gynecologist_profile, name='gynecologist_profile'),
    # path('profile/edit/', edit_profile, name='edit_profile'),  
]