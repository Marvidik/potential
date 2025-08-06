from django.urls import path
from .views import register, login,create_consultation,get_user_consultations,get_notifications,update_user_account

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),

    path('consultations/', create_consultation, name='create-consultation'),
    path('consultations/my/', get_user_consultations, name='user-consultations'),

    path('notifications/', get_notifications, name='get-notifications'),

    path('account/update/', update_user_account, name='update-account'),
]
