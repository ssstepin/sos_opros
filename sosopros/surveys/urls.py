from django.urls import path

from .views import *

urlpatterns = [
    path('login/', MyLoginView.as_view(template_name="users/login.html"), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('home/', home, name='home'),
    path('surveys/', get_user_surveys, name='surveys'),
    path('surveys/<int:pk>/', survey_details, name='survey_details'),
    path("surveys/<int:pk>/edit/", edit_survey, name='survey_edit'),
    path("surveys/create", create_survey, name='survey_create'),
    path("surveys/<int:pk>/question/", create_question, name='question_create'),
    path("surveys/<int:spk>/question/<int:qpk>/option", create_option, name='option_create'),
]
