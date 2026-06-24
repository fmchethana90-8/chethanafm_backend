from django.urls import path
from .views import ProgramScheduleView

urlpatterns = [
    path('schedule/', ProgramScheduleView.as_view()),
]