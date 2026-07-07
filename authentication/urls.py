from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    SecurityQuestionsListView,
    GetSecurityQuestionView,
    VerifySecurityAnswerView,
    ResetPasswordView,
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('security-questions/', SecurityQuestionsListView.as_view()),
    path('get-security-question/', GetSecurityQuestionView.as_view()),
    path('verify-answer/', VerifySecurityAnswerView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]