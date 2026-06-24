from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import ProgramSchedule
from .serializers import ProgramScheduleSerializer

class ProgramScheduleView(ListAPIView):
    queryset = ProgramSchedule.objects.all()
    serializer_class = ProgramScheduleSerializer