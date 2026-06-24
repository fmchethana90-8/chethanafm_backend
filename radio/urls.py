from django.urls import path
from .views import LiveProgramView

urlpatterns= [
    path('live/',LiveProgramView.as_view()),
]