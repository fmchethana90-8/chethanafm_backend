from django.urls import path
from .views import RegisterView, LoginView, ProfileView, CheckPhoneView, ResetPasswordView

urlpatterns = [
    path('register/',      RegisterView.as_view(),     name='auth-register'),
    path('login/',         LoginView.as_view(),         name='auth-login'),
    path('profile/',       ProfileView.as_view(),       name='auth-profile'),
    path('check-phone/',   CheckPhoneView.as_view(),   name='auth-check-phone'),
    path('reset-password/', ResetPasswordView.as_view(), name='auth-reset-password'),
]