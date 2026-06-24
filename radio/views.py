from django.shortcuts import render

# Create your views here.
from rest_framework.generics import RetrieveAPIView
from .models import LiveProgram
from .serializers import LiveProgramSerializer

class LiveProgramView(RetrieveAPIView):

    serializer_class = LiveProgramSerializer

    def get_object(self):
        
        obj, created = LiveProgram.objects.get_or_create(id=1)

        return obj