from django.db import models

# Create your models here.



class Doctor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)  # instead of specialization
    phone = models.CharField(max_length=15, blank=True, null=True)
    about = models.TextField()
    image = models.ImageField(blank=True, null=True)  # store image URL or media file

    def __str__(self):
        return self.name
    


