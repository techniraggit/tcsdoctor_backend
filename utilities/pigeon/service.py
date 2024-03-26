import json
import os
import requests
from django.conf import settings
from twilio.rest import Client


def send_sms(mobile, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=f"{message}", from_=settings.TWILIO_NUMBER, to=f"+91{mobile}"
        )
        return True
    except Exception as e:
        print(e)
        return False


def send_email(
    subject: str, body: str, recipients: list, file_content:bytes=None, file_name:str=None
):
    CEP_API_URL = os.getenv("CEP_API_URL")
    CEP_AUTHORIZATION = os.getenv("CEP_AUTHORIZATION")
    CEP_SYSTEM_ID = os.getenv("CEP_SYSTEM_ID")
    CEP_MESSAGE_ID = os.getenv("CEP_MESSAGE_ID")
    headers = {
    'Authorization': CEP_AUTHORIZATION,
    'Content-Type': 'application/json'
    }
    data = dict(
        sysid = CEP_SYSTEM_ID,
        msgid = CEP_MESSAGE_ID,
        emailid = recipients[0],
        subject = subject,
        body = body
        )
    if file_content and file_name:
        data["attachments"] = [
            {
                "fileName": file_name,
                "fileContent": file_content,
            }
        ]
    response = requests.post(CEP_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return True
    return False
    """
    Sends an email using a third-party API with the specified parameters.

    Parameters:
    - subject (str): The subject of the email.
    - body (str): The body/content of the email.
    - recipients (list): A list of email addresses to which the email will be sent.
    - file_content (bytes, optional): The content of the file to be attached to the email.
    - file_name (str, optional): The name of the file to be attached.

    Returns:
    - bool: True if the email is sent successfully, False otherwise.

    Note:
    - The email is sent using the Falcon API, and the API key, API URL, and other settings
      are retrieved from the Django settings module.
    - If file_content and file_name are provided, the function attaches the specified file
      to the email.
    """
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
        "attachments": None,
    }
    if file_content and file_name:
        params["attachments"] = [
            {
                "fileName": file_name,
                "fileContent": file_content,
            }
        ]
    headers = {"content-type": "application/json", "api_key": settings.FALCON_API_KEY}
    response = requests.post(
        settings.FALCON_API_URL, data=json.dumps(params), headers=headers
    )

    if response.status_code // 100 == 2:
        return True
    else:
        return False
