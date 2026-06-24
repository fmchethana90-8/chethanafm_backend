from rest_framework import serializers
from .models import ProgramSchedule

class ProgramScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramSchedule
        fields = '__all__'