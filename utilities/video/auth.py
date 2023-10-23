from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from django.conf import settings

twilio_account_sid = settings.TWILIO_ACCOUNT_SID
twilio_api_key = settings.TWILIO_API_KEY
twilio_api_secret = settings.TWILIO_API_SECRET


def get_access_token(identity, room_name):
    # Create Access Token with credentials
    token = AccessToken(
        twilio_account_sid, twilio_api_key, twilio_api_secret, identity=identity
    )

    # Create a Video grant and add to token
    video_grant = VideoGrant(room=room_name)
    token.add_grant(video_grant)

    # Return token info as JSON
    return token.to_jwt()
