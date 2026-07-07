from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import SECURITY_QUESTIONS

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    security_answer = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'name',
            'phone_number',
            'password',
            'confirm_password',
            'security_question',
            'security_answer',
        ]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Enter a valid 10-digit phone number.")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def validate_security_question(self, value):
        valid_keys = [q[0] for q in SECURITY_QUESTIONS]
        if value not in valid_keys:
            raise serializers.ValidationError("Invalid security question.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        security_answer = validated_data.pop('security_answer').strip().lower()
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            password=validated_data['password'],
            security_question=validated_data.get('security_question'),
            security_answer=security_answer,
        )
        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            phone_number=data['phone_number'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("Invalid phone number or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account has been disabled.")
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number']


class GetSecurityQuestionSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("No account found with this phone number.")
        return value


class VerifySecurityAnswerSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    security_answer = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(phone_number=data['phone_number'])
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this phone number.")

        if user.security_answer != data['security_answer'].strip().lower():
            raise serializers.ValidationError("Security answer is incorrect.")

        data['user'] = user
        return data


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    security_answer = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        try:
            user = User.objects.get(phone_number=data['phone_number'])
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this phone number.")

        if user.security_answer != data['security_answer'].strip().lower():
            raise serializers.ValidationError("Security answer is incorrect.")

        data['user'] = user
        return data