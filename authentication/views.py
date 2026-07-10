from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from .models import SECURITY_QUESTIONS
from .validators import get_valid_country_codes
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    GetSecurityQuestionSerializer,
    VerifySecurityAnswerSerializer,
    ResetPasswordSerializer,
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
            "user": UserSerializer(user).data
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
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CountryCodesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(get_valid_country_codes())


class SecurityQuestionsListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        questions = [
            {"key": q[0], "question": q[1]}
            for q in SECURITY_QUESTIONS
        ]
        return Response(questions)


class GetSecurityQuestionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GetSecurityQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        if not user.security_question:
            return Response(
                {"error": "No security question set for this account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        question_text = dict(SECURITY_QUESTIONS).get(user.security_question, "")

        return Response({
            "phone_number": user.phone_number,
            "country_code": user.country_code,
            "security_question": user.security_question,
            "question_text": question_text,
        })


class VerifySecurityAnswerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifySecurityAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "message": "Answer verified. You can now reset your password."
        })


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        Token.objects.filter(user=user).delete()

        return Response(
            {"message": "Password reset successfully. Please login again."},
            status=status.HTTP_200_OK
        )