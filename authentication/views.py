import jwt
from rest_framework import generics,status,permissions,parsers
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from .serializers import *
from .utils import SendActivationEmail
from django.conf import settings

secret = settings.SECRET_KEY


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = User.objects.get(email=request.data.get('email'))
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            reversed_url=reverse('verify-email')
            absolut_path = 'http://' + current_site + reversed_url  + str(token) + '/'
            data = {'path':absolut_path,'user':user}
            SendActivationEmail.send_email(data)

            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    def post(self,request):
        token=request.data.get('token')
        try:
            payload = jwt.decode(token,secret,algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
                return Response({'activation':'Your account successfuly activated .'},status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error':'Activation expired.'},status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return Response({'error':'Invalid token .'},status=status.HTTP_400_BAD_REQUEST)


class UserAPI(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,*args,**kwargs):
        serializer = self.serializer_class(instance=request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def delete(self,request):
        user = request.user
        user.delete()
        return Response({'success':'Account deleted successfuly. '},status=200)


class PasswordResetAPI(generics.GenericAPIView):

    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=request.data.get('email'))
        user.is_active = False
        user.save(force_update=True)

        
        uid64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user=user)

        curr_site = get_current_site(request).domain

        absolut_path = 'http://'+curr_site+'password-reset-confirm/'+uid64+'/'+token+'/'
        data = {
            'user':user,
            'path':absolut_path
        }
        SendActivationEmail.send_reset_email(data=data)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmAPI(generics.GenericAPIView):
    parser_classes = [parsers.JSONParser]
    serializer_class = PasswordResetConfirmSerializer

    def post(self,request,**kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:

            id = force_text(urlsafe_base64_decode(kwargs['uid64']))
            user = User.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user,kwargs['token']):
                return Response({'error':'Token is not valid, please requst new one. '})

            user.set_password(request.data.get('password'))
            user.is_active = True
            user.save(force_update=True)
            return Response({'success':'Password successfuly changed. '},status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            if not PasswordResetTokenGenerator().check_token(user,kwargs['token']):
                return Response({'error':'Token is not valid, please requst new one. '})

        return Response(serializer.data,status=status.HTTP_200_OK)


class ChangePasswordAPI(generics.GenericAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self,request):
        self.get_serializer_context()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(request.data.get('old_password')):
            return Response({'error':'Old password is incorrect. '},status=status.HTTP_400_BAD_REQUEST)
        user.set_password(request.data.get('new_password'))
        user.save()

        return Response({'success':'Password updated successfuly. '},status=200)
        

class LogoutAPI(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)