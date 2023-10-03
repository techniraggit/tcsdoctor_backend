from django.test import TestCase

# Create your tests here.
import uuid
from django.http import JsonResponse
from twilio.jwt.access_token.grants import VideoGrant
from twilio.jwt.access_token import AccessToken
from django.conf import settings

def create_video_room(request):
    # Create a unique room name for the video call
    room_name = f"consult_{uuid.uuid4()}"
    identity = str(uuid.uuid4())

    token = AccessToken(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
        identity,
        nbf="",
        valid_until="",
    )
    token.add_grant(VideoGrant(room=room_name))

    matting_url = f"http://127.0.0.1:9000/doctor/join_call?identity={identity}&roomName={room_name}"
    # Return the token as a JSON response
    return JsonResponse({"token": token.to_jwt(), "room_name": room_name})
