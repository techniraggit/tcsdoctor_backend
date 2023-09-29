import json
import requests
from django.core.mail import (
    EmailMultiAlternatives,
    EmailMessage,
)
from django.conf import settings
from twilio.rest import Client
from rest_framework.response import Response

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def send_sms(mobile, message):
    try:
        message = client.messages.create(
            body=f"{message}", from_=settings.TWILIO_NUMBER, to=f"+91{mobile}"
        )
        return True
    except Exception as e:
        print(e)
        return False


# Send Email using Falcon API
def send_api_email(subject: str, body: str, recipients: list, attachments=None):
    personalizations = [
        {"recipient": recipient, "recipient_cc": ()} for recipient in recipients
    ]

    params = {
        "personalizations": personalizations,
        "from": {
            "fromEmail": settings.FALCON_FROM_EMAIL,
            "fromName": settings.FALCON_FROM_NAME,
        },
        "subject": subject,
        "settings": {
            "footer": 1,
            "clicktrack": 0,
            "opentrack": 1,
            "unsubscribe": 0,
            "bcc": "",
        },
        "replyToId": settings.FALCON_REPLY_TO_ID,
        "content": body,
        "attachments": attachments,
    }
    headers = {"content-type": "application/json", "api_key": settings.FALCON_API_KEY}
    response = requests.post(
        settings.FALCON_API_URL, data=json.dumps(params), headers=headers
    )
    if response.status_code // 100 == 2:
        return True
    else:
        return False


# Send Email SMTP


def send_smtp_email(
    subject, message, recipients, attachment=None, file_type=None, file_name=None
):
    try:
        if attachment:
            email = EmailMessage(
                subject, message, settings.DEFAULT_FROM_EMAIL, recipients
            )
            email.attach(file_name, attachment, file_type)
        else:
            email = EmailMultiAlternatives(
                subject, message, settings.DEFAULT_FROM_EMAIL, recipients
            )
            email.attach_alternative(message, "text/html")

        email.send()
        return True
    except:
        return False


def send_email(
    subject: str,
    message: str,
    recipients: list,
    attachments=None,
    file_type=None,
    file_name=None,
):
    if settings.IS_SMTP:
        send_smtp_email(
            subject,
            message,
            recipients,
            attachment=None,
            file_type=None,
            file_name=None,
        )
    else:
        send_api_email(subject, message, recipients)
