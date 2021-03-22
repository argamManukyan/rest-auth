from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('verify-email/',VerifyEmail.as_view(),name='verify-email'),
    path('login/',TokenObtainPairView.as_view(),name='login'),
    path('refresh/',TokenRefreshView.as_view(),name='refresh'),
    path('profile/',UserAPI.as_view(),name='user-profile'),
    path('password-reset/',PasswordResetAPI.as_view(),name='password-reset'),
    path('password-reset-confirm/<uid64>/<token>/',PasswordResetConfirmAPI.as_view(),name='password-reset-confirm'),
    path('change-password/',ChangePasswordAPI.as_view(),name='change-password'),
    path('logout/',LogoutAPI.as_view(),name='logout')
]
