from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken

class UserManager(BaseUserManager):

    def create_user(self,**extra_fields):

        email = self.normalize_email(email=extra_fields['email'])
        del extra_fields['email']
        user = self.model(email=email,**extra_fields)
        user.set_password(extra_fields['password'])
        user.save()
        return user

    def create_staff_user(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields['email']:
            raise ValidationError({'email': 'The field email is required .'})
        email = self.normalize_email(email=extra_fields['email'])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

    def create_superuser(self,password=None, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields['email']:
            raise ValidationError({'email': 'The field email is required .'})
        email = self.normalize_email(email=extra_fields['email'])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()


class User(AbstractUser, PermissionsMixin):

    first_name = models.CharField(max_length=50,blank=True,null=True)
    last_name = models.CharField(max_length=50,blank=True,null=True)
    username = models.CharField(max_length=255,unique=True,blank=True)
    email = models.CharField(unique=True,max_length=255)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name','is_staff','is_active']

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def tokens(self):
        token = RefreshToken.for_user(self)
        return {
            'access':str(token.access_token),
            'refresh':str(token)
            }

    def __str__(self):
        return self.first_name


