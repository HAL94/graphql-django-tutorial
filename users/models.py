
import re
from django.db import models
from django.utils import timezone

from core.utils import AUTH_METHOD_CHOICES, AuthMethod
import phonenumbers
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class ValidateEmail(object):
    def __init__(self,  email=None) :
        self.to_email = email


    def is_valid(self):        
        # Make a regular expression for validating an Email
        regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        return re.fullmatch(regex, self.to_email)
        

class UserManager(BaseUserManager):
    def create_user(self, auth_method, username, password, email=None, phone=None):
        """
        Creates and saves a User with the given auth_method, username and password.
        """
        if not username:
            raise ValueError('A username must be provided, either a phone or an email')

        
        user = self.model(auth_method=auth_method, username=username, email=email, phone=phone)
        
        if auth_method == AuthMethod.EMAIL:
            email_validator = ValidateEmail(username)
            if not email_validator.is_valid():
                raise ValueError('Email provided is invalid')
            
            user.email = username
        elif auth_method == AuthMethod.MOBILE:
            number = phonenumbers.parse(username)
            if not phonenumbers.is_valid_number(number):
                raise ValueError('Mobile Phone provided is invalid')
            user.phone = username

        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(username=username,password=password, auth_method=AuthMethod.EMAIL)
        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    auth_method = models.CharField(max_length=10, choices=AUTH_METHOD_CHOICES, blank=True)
    username = models.CharField(blank=False, max_length=255, verbose_name="username", unique=True)
    phone = models.CharField(blank=True, verbose_name='phone', max_length=17, null=True)
    email = models.CharField(blank=True, verbose_name='email address', max_length=255, null=True)
    
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(blank=False, default=False)

    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    
    USERNAME_FIELD = "username"    
    objects = UserManager()
