import re
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import SECURITY_QUESTIONS
from .validators import validate_phone_number, VALID_COUNTRY_CODES

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    security_answer = serializers.CharField(write_only=True)
    country_code = serializers.CharField(default='+91')

    class Meta:
        model = User
        fields = [
            'name',
            'country_code',
            'phone_number',
            'password',
            'confirm_password',
            'security_question',
            'security_answer',
        ]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError("Name must contain letters only.")
        return value

    def validate_country_code(self, value):
        if value not in VALID_COUNTRY_CODES:
            raise serializers.ValidationError(
                f"Invalid country code. Valid codes: {', '.join(VALID_COUNTRY_CODES)}"
            )
        return value

    def validate_security_question(self, value):
        valid_keys = [q[0] for q in SECURITY_QUESTIONS]
        if value not in valid_keys:
            raise serializers.ValidationError("Invalid security question.")
        return value

    def validate(self, data):
        # Password match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Phone number validation
        country_code = data.get('country_code', '+91')
        phone_number = data.get('phone_number', '')

        is_valid, error = validate_phone_number(country_code, phone_number)
        if not is_valid:
            raise serializers.ValidationError({"phone_number": error})

        # Check uniqueness with country code
        full_phone = phone_number
        if User.objects.filter(
            phone_number=full_phone,
            country_code=country_code
        ).exists():
            raise serializers.ValidationError({
                "phone_number": "This phone number is already registered."
            })

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        security_answer = validated_data.pop('security_answer').strip().lower()

        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            password=validated_data['password'],
            country_code=validated_data.get('country_code', '+91'),
            security_question=validated_data.get('security_question'),
            security_answer=security_answer,
        )
        return user


class LoginSerializer(serializers.Serializer):
    country_code = serializers.CharField(default='+91')
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_country_code(self, value):
        if value not in VALID_COUNTRY_CODES:
            raise serializers.ValidationError("Invalid country code.")
        return value

    def validate(self, data):
        country_code = data.get('country_code', '+91')
        phone_number = data.get('phone_number', '')
        password = data.get('password', '')

        # Validate phone format first
        is_valid, error = validate_phone_number(country_code, phone_number)
        if not is_valid:
            raise serializers.ValidationError({"phone_number": error})

        # Try to authenticate
        user = authenticate(
            phone_number=phone_number,
            password=password
        )

        # Also check country code matches
        if user and user.country_code != country_code:
            user = None

        if not user:
            raise serializers.ValidationError(
                "Invalid phone number or password."
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "This account has been disabled."
            )

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'country_code', 'phone_number']


class GetSecurityQuestionSerializer(serializers.Serializer):
    country_code = serializers.CharField(default='+91')
    phone_number = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(
                phone_number=data['phone_number'],
                country_code=data['country_code']
            )
            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No account found with this phone number."
            )
        return data


class VerifySecurityAnswerSerializer(serializers.Serializer):
    country_code = serializers.CharField(default='+91')
    phone_number = serializers.CharField()
    security_answer = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(
                phone_number=data['phone_number'],
                country_code=data['country_code']
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No account found with this phone number."
            )

        if user.security_answer != data['security_answer'].strip().lower():
            raise serializers.ValidationError("Security answer is incorrect.")

        data['user'] = user
        return data


class ResetPasswordSerializer(serializers.Serializer):
    country_code = serializers.CharField(default='+91')
    phone_number = serializers.CharField()
    security_answer = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        try:
            user = User.objects.get(
                phone_number=data['phone_number'],
                country_code=data['country_code']
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No account found with this phone number."
            )

        if user.security_answer != data['security_answer'].strip().lower():
            raise serializers.ValidationError("Security answer is incorrect.")

        data['user'] = user
        return data