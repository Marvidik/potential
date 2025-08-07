from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),

    path('consultations/', create_consultation, name='create-consultation'),
    path('consultations/my/', get_user_consultations, name='user-consultations'),

    path('notifications/', get_notifications, name='get-notifications'),

    path('account/update/', update_user_account, name='update-account'),

    path('dashboard/', get_user_dashboard, name='user-dashboard'),

    path('delete-notification/<int:id>/', delete_notification, name='delete-notification'),
    path('delete-consultation/<int:id>/', delete_consultation, name='delete-consultation'),
]
