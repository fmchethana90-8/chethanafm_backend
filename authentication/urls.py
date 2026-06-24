from django.urls import path
from .views import (RegisterView,LoginView,ProfileView,CheckPhoneView,ResetPasswordView)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('check-phone/', CheckPhoneView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]