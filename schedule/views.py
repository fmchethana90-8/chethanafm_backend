
from rest_framework.generics import ListAPIView
from .models import ProgramSchedule
from .serializers import ProgramScheduleSerializer
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

class SchedulePagination(PageNumberPagination):

    page_size = 50

class ProgramScheduleView(ListAPIView):

    permission_classes = [AllowAny]
    queryset = ProgramSchedule.objects.all()
    serializer_class = ProgramScheduleSerializer
    pagination_class = SchedulePagination