from django.contrib import admin
from .models import User

@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):

    list_display = ['id','email','first_name','is_staff']
