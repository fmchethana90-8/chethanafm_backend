from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .serializers import SendNotificationSerializer
from .firebase import send_push_notification
from .models import NotificationLog

class SendNotificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data['title']
        body = serializer.validated_data['body']

        send_push_notification(title, body)
        NotificationLog.objects.create(title=title, body=body)

        return Response({"status": "sent"})