from django.urls import path ,include
from . import views
from patient.views import patient_dashboard  
from gync.views import doctor_dashboard  

app_name = 'accounts'  

urlpatterns = [
    path('select-role/', views.select_role_view, name='select_role'),
    path('signup/<str:role>/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/upload_picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('profile/remove_picture/', views.remove_profile_picture, name='remove_profile_picture'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('recommend-doctor/', views.recommend_doctor_view, name='recommend_doctor'),
    path('doctor/<int:doctor_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('faq/', views.faq_page, name='faq_page'),
    path('faq/add_question/', views.add_question, name='add_question'),
    path('faq/add_answer/<int:question_id>/', views.add_answer, name='add_answer'),
    path("faq/toggle_like_question/", views.upvote_question, name="upvote_question"),
    path("faq/toggle_like_answer/", views.upvote_answer, name="upvote_answer"),
    path("your_questions/", views.your_questions, name="your_questions"),
    path('delete_question/<int:qus_id>/', views.delete_question, name='delete_question'),
    path('delete_answer/<int:ans_id>/', views.delete_answer, name='delete_answer'),
    path('patient/', include('patient.urls', namespace='patient')),
    path('gync/', include('gync.urls', namespace='gync')),
    path('logout/',views.custom_logout_view, name='logout'),
]