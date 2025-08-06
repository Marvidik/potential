# urls.py
from django.urls import path
from .views import get_doctors

urlpatterns = [
    path('doctors/', get_doctors, name='get-doctors'),
    
]
