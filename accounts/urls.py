from django.urls import path ,include
from . import views
from .views import signup_view, select_role_view, recommend_doctor_view
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from patient.views import patient_dashboard  
from gync.views import doctor_dashboard  
from .views import faq_page, add_question, add_answer, login_view, upvote_question, upvote_answer ,profile_view, upload_profile_picture, remove_profile_picture, your_questions,delete_question, delete_answer
from .views import gynecologist_profile_view, submit_feedback
from .views import edit_profile

app_name = 'accounts'  # Define the app namespace

urlpatterns = [
    path('profile/', views.profile_view, name='profile_view'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('doctor/<int:doctor_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    # path('doctor/<int:doctor_id>/', views.profile_view, name='doctor_profile'),
    # path('doctor/<int:doctor_id>/feedback/', submit_feedback, name='submit_feedback'),
    path('recommend-doctor/', views.recommend_doctor_view, name='recommend_doctor'),
    # path('doctor/<int:doctor_id>/', views.gynecologist_profile_view, name='doctor_profile'),
   
    # path('doctor/<int:doctor_id>/', views.gynecologist_profile_view, name='doctor_profile'),
    # path('doctor/<int:doctor_id>/feedback/', submit_feedback_view, name='submit_feedback'),
    # path('profile/', profile_view, name='profile_view'),
    path('profile/upload_picture/', upload_profile_picture, name='upload_profile_picture'),
    path('profile/remove_picture/', remove_profile_picture, name='remove_profile_picture'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', login_view, name='login'),
    path('select-role/', select_role_view, name='select_role'),
    path('signup/<str:role>/', signup_view, name='signup'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    # path('recommend-doctor/', recommend_doctor_view, name='recommend_doctor'),
    path('faq/', faq_page, name='faq_page'),
    path('faq/add_question/', add_question, name='add_question'),
    path('faq/add_answer/<int:question_id>/', add_answer, name='add_answer'),
    path("faq/toggle_like_question/", upvote_question, name="upvote_question"),
    path("faq/toggle_like_answer/", upvote_answer, name="upvote_answer"),
    path("your_questions/", your_questions, name="your_questions"),
    path('delete_question/<int:qus_id>/', delete_question, name='delete_question'),
    path('delete_answer/<int:ans_id>/', delete_answer, name='delete_answer'),

    path('patient/', include('patient.urls', namespace='patient')),
    path('gync/', include('gync.urls', namespace='gync')),
]


