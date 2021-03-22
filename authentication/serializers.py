from rest_framework import serializers
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from django.contrib.auth import get_user_model
from rest_framework.exceptions import  ValidationError
from datetime import datetime
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=15, write_only=True)
    re_password = serializers.CharField(min_length=6, max_length=15, write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','password','re_password','username']

    def validate(self, attrs):
        password = attrs['password']
        re_password = attrs['re_password']
        if not attrs.get('username'):
            attrs['username'] = str(attrs.get('first_name')).lower() + str(datetime.now()).split(':')[1]
        if re_password != password:
            raise ValidationError({"error": 'Passwords is not similar'})
        return attrs

    def create(self, validated_data):
        del validated_data['re_password']
        user = User.objects.create_user(**validated_data)

        return user

class VerifyEmailSerializer(serializers.Serializer):

    token = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','username','first_name','last_name','is_staff','is_active']


class PasswordResetSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email','')
        if not len(email):
            return ValidationError({'error':'Email is required. '})
                
        return attrs

class PasswordResetConfirmSerializer(serializers.Serializer):

    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)
 
    def validate(self, attrs):
        password = attrs.get('password')
        re_password = attrs.get('re_password')

        if re_password != password:
            raise ValidationError({'error':'Two passwords is not similar. '})
        
        return attrs

class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    re_new_password = serializers.CharField(write_only=True)
 
    def validate(self, attrs):
        password = attrs.get('password')
        re_password = attrs.get('re_password')
        print(self.context.get('request'))
        if re_password != password:
            raise ValidationError({'error':'Two passwords is not similar. '})
        
        return attrs


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token':'Invalid token. '
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh')
        
        return attrs

    def save(self, **kwargs):
    
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')