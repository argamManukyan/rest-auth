from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
email_admin = settings.EMAIL_HOST_USER


class SendActivationEmail:

    @staticmethod
    def send_email(data):
        user = data.get('user')
        message = render_to_string('authentication/email_activation.html',{
            'email':user.email,
            'username':user.username,
            'link':data.get('path')
        })
        send_mail(subject='Verify email',message=message,from_email=email_admin,
        recipient_list=[user.email],fail_silently=False)
    
    @staticmethod
    def send_reset_email(data):
        user = data.get('user')
        message = render_to_string('authentication/password_reset.html',{
            'email':user.email,
            'username':user.username,
            'link':data.get('path')
        })
        send_mail(subject='Password change',message=message,from_email=email_admin,
        recipient_list=[user.email],fail_silently=False)
