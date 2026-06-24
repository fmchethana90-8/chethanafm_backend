import firebase_admin
from firebase_admin import credentials, messaging
import os
from django.conf import settings

cred_path = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def send_push_notification(title, body):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        topic="all_users",
    )
    return messaging.send(message)