
from pickle import FALSE
from django.db import models
from core.utils import AUTH_METHOD_CHOICES
# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):    
    auth_method = models.CharField(max_length=10, choices=AUTH_METHOD_CHOICES, blank=True)
    username = models.CharField(blank=False, max_length=255, verbose_name="username", unique=True)
    password = models.CharField(blank=False, max_length=20)
    phone = models.CharField(blank=False, max_length=17, unique=True)

    USERNAME_FIELD = "username"