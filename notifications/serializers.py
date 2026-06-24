from rest_framework import serializers

class SendNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    body = serializers.CharField()