from twilio.jwt.access_token import AccessToken, AccessTokenGrant
from twilio.jwt.access_token.grants import VideoGrant
from django.conf import settings
from doctor.models import Appointments
from datetime import timedelta

twilio_account_sid = settings.TWILIO_ACCOUNT_SID
twilio_api_key = settings.TWILIO_API_KEY
twilio_api_secret = settings.TWILIO_API_SECRET


def get_access_token(identity, room_name):
    try:
        token = AccessToken(
            twilio_account_sid, twilio_api_key, twilio_api_secret, identity=identity
        )

        video_grant = VideoGrant(room=room_name)
        token.add_grant(video_grant)
        return True, token.to_jwt()
    except Exception as e:
        return False, ""

