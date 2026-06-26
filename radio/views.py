
from rest_framework.generics import RetrieveAPIView
from .models import LiveProgram
from .serializers import LiveProgramSerializer
from django.http import Http404
from rest_framework.permissions import AllowAny

class LiveProgramView(RetrieveAPIView):

    permission_classes = [AllowAny]
    serializer_class = LiveProgramSerializer

    def get_object(self):

        try:

            return LiveProgram.objects.filter(is_live=True).latest('id')
        
        except LiveProgram.DoesNotExist:

            raise Http404("No live program is currently active.")