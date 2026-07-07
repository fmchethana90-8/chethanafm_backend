from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import SECURITY_QUESTIONS
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


class SecurityQuestionsListView(APIView):
    """
    Returns all available security questions.
    Flutter shows these as a dropdown during registration.
    """
    def get(self, request):
        questions = [
            {"key": q[0], "question": q[1]}
            for q in SECURITY_QUESTIONS
        ]
        return Response(questions)


class GetSecurityQuestionView(APIView):
    """
    Step 1 of forgot password.
    Flutter sends phone number → gets back which security question the user set.
    """
    def post(self, request):
        serializer = GetSecurityQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        user = User.objects.get(phone_number=phone_number)

        if not user.security_question:
            return Response(
                {"error": "No security question set for this account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find the question text from the key
        question_text = dict(SECURITY_QUESTIONS).get(user.security_question, "")

        return Response({
            "phone_number": phone_number,
            "security_question": user.security_question,
            "question_text": question_text,
        })


class VerifySecurityAnswerView(APIView):
    """
    Step 2 of forgot password.
    Flutter sends phone + answer → verified or rejected.
    """
    def post(self, request):
        serializer = VerifySecurityAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Answer verified. You can now reset your password."})


class ResetPasswordView(APIView):
    """
    Step 3 of forgot password.
    Flutter sends phone + answer + new password → password updated.
    """
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