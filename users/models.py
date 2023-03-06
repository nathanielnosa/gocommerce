from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model): 
    SEX = (
        ('M','Male'),
        ('F','Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=250)
    username = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=50, choices=SEX)
    profile_pix = models.ImageField(upload_to='profile',blank=True)

    def __str__(self):
        return f'{self.username}'