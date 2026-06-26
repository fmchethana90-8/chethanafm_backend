from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.core import signing

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileSerializer,       # ← added
    ResetPasswordSerializer
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data        # no phone_number
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data        # no phone_number
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)   # phone_number included


class CheckPhoneView(APIView):
    """
    Flutter calls this first to check if phone number exists
    before sending OTP via Firebase.
    Returns a short-lived reset_token if the phone number is found.
    Flutter must pass this token to ResetPasswordView after OTP verification.
    """
    permission_classes = [AllowAny]

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

        reset_token = signing.dumps(
            {'phone': phone_number},
            salt='password-reset',
        )

        return Response(
            {
                "message": "Phone number found. OTP can be sent.",
                "reset_token": reset_token,
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    """
    Flutter calls this AFTER Firebase OTP is verified successfully.
    Requires the reset_token received from CheckPhoneView.
    Token expires in 10 minutes — if expired, user must restart the flow.
    """
    permission_classes = [AllowAny]

    RESET_TOKEN_MAX_AGE = 600  # 10 minutes in seconds

    def post(self, request):
        reset_token = request.data.get('reset_token', '')
        if not reset_token:
            return Response(
                {"error": "Reset token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = signing.loads(
                reset_token,
                salt='password-reset',
                max_age=self.RESET_TOKEN_MAX_AGE,
            )
        except signing.SignatureExpired:
            return Response(
                {"error": "Reset token has expired. Please restart the password reset process."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except signing.BadSignature:
            return Response(
                {"error": "Invalid reset token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']

        if payload.get('phone') != phone_number:
            return Response(
                {"error": "Token does not match the provided phone number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_password = serializer.validated_data['new_password']

        user = User.objects.get(phone_number=phone_number)
        user.set_password(new_password)
        user.save()

        Token.objects.filter(user=user).delete()

        return Response(
            {"message": "Password reset successfully. Please login again."},
            status=status.HTTP_200_OK
        )