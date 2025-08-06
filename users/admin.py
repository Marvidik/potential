from django.contrib import admin
from .models import Consultation, UserInfo,Notification
# Register your models here.
admin.site.site_header = "Potential Admin"
admin.site.site_title = "Potential Admin Portal"



admin.site.index_title = "Welcome to Potential Admin Portal"

admin.site.register(Consultation)
admin.site.register(UserInfo)
admin.site.register(Notification)