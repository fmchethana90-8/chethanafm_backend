from rest_framework import serializers

from .models import LiveProgram

class LiveProgramSerializer(serializers.ModelSerializer):

    class Meta:
        
        model=LiveProgram
        fields= '__all__'