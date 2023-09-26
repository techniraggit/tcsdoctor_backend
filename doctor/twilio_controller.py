# twilio_controller.py
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from django.conf import settings


def generate_video_access_token(identity, room_name):
    # Create an AccessToken for the participant
    token = AccessToken(settings.TWILIO_ACCOUNT_SID, identity)
    token.add_grant(VideoGrant(room=room_name))
    return token.to_jwt()
