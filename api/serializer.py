from .models import Staff,Task,Admin,DirectorsTask,PasswordResetOTP
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class AdminSerializer(ModelSerializer):
    class Meta:
        model=Admin
        fields="__all__"

class SignupSerializer(serializers.Serializer):
    dept=serializers.CharField(allow_null=True)
    name=serializers.CharField(allow_null=True)
    email=serializers.EmailField(allow_null=True)
    password=serializers.CharField(allow_null=True)
    role=serializers.CharField(allow_null=True, required=False)

class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField(allow_null=True)
    password=serializers.CharField(allow_null=True)

class AdminLoginSerializer(serializers.Serializer):
    email=serializers.EmailField(allow_null=True)
    password=serializers.CharField(allow_null=True)


        
class StaffSerializer(ModelSerializer):
    class Meta:
        model=Staff
        fields="__all__"
        
class TaskSerializer(ModelSerializer):
    class Meta:
        model=Task
        fields="__all__"

class DirectorsTaskSerializer(ModelSerializer):
    staff_name = serializers.CharField(source='staff.Name', read_only=True)
    staff_dpt = serializers.CharField(source='staff.dpt', read_only=True)
    class Meta:
        model=DirectorsTask
        fields="__all__"

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    password = serializers.CharField()
