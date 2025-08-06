from django.db import models
from django.contrib.auth.models import User
from .utils import generate_unique_visitor_id

# Create your models here.

class UserInfo(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    address= models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    display_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.address}"
    


class Consultation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations')
    visitor_id = models.PositiveIntegerField(unique=True, editable=False)
    doctor_name = models.CharField(max_length=255)
    doctor_department = models.CharField(max_length=255)
    visit_date = models.DateField()
    visit_time = models.TimeField()
    reason_for_visit = models.TextField()
    status=models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.visitor_id:  # Only generate if it's empty
            self.visitor_id = generate_unique_visitor_id()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.doctor_name} - {self.visit_date}"
    


class Notification(models.Model):
    img = models.ImageField(blank=True, null=True)  # image URL
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title