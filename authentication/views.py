from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ResetPasswordSerializer
)

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CheckPhoneView(APIView):
    """
    Flutter calls this first to check if phone number exists
    before sending OTP via Firebase.
    """
    def post(self, request):
        phone_number = request.data.get('phone_number', '')
        if not phone_number:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        exists = User.objects.filter(phone_number=phone_number).exists()
        if not exists:
            return Response(
                {"error": "No account found with this phone number."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"message": "Phone number found. OTP can be sent."},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    """
    Flutter calls this AFTER Firebase OTP is verified successfully.
    Django just updates the password — no OTP handling needed here.
    """
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        new_password = serializer.validated_data['new_password']

        user = User.objects.get(phone_number=phone_number)
        user.set_password(new_password)
        user.save()

        # Delete old token so user has to login again with new password
        Token.objects.filter(user=user).delete()

        return Response(
            {"message": "Password reset successfully. Please login again."},
            status=status.HTTP_200_OK
        )