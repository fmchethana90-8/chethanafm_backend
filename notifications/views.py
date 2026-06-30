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

        try:
            send_push_notification(title, body)
            success = True
            error_msg = None
        except Exception as e:
            success = False
            error_msg = str(e)

        NotificationLog.objects.create(title=title, body=body)  # Always log

        if not success:

            return Response({"status": "failed", "error": error_msg}, status=500)
        
        return Response({"status": "sent"})  