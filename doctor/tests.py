from django.test import TestCase

# Create your tests here.
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from twilio.jwt.access_token.grants import VideoGrant
from twilio.jwt.access_token import AccessToken
from administrator.models import UserPushNotification
from rest_framework.decorators import api_view
from core.mixins import DoctorViewMixin
from core.decorators import token_required
from utilities.utils import (
    is_valid_date,
    is_valid_email,
    is_valid_phone,
)


from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from django.conf import settings
from django.db import transaction
from doctor.models import (  # Doctor Models
    Users,
    Patients,
    Appointments,
)
from doctor.serializers import (  # Doctor Serializers
    AppointmentsSerializer,
)


from utilities.algo import get_available_time_slots


# # views.py

# from .models import VideoRoom

# class GenerateVideoAccessToken(APIView):
#     def get(self, request):
#         identity = request.query_params.get('identity')
#         room_name = request.query_params.get('room_name')
#         # token = AccessToken(account_sid="AC70ea0564259686e89e4a1c58f3bb98e2",
#         #                     token="dcd4a31c42d209c6df17fc3ebdf539fd",
#         #                     identity="O4x40EexJbNUnDzwf5iY8rzcUTz5gMnq",
#         #                     )
#         token = AccessToken(
#             "AC70ea0564259686e89e4a1c58f3bb98e2",
#             "dcd4a31c42d209c6df17fc3ebdf539fd",
#             "O4x40EexJbNUnDzwf5iY8rzcUTz5gMnq"
#         )
#         token.add_grant(VideoGrant(room=room_name))
#         print(token)

#         return Response({'token': token.to_jwt()})


def join_call(request):
    context = {"identity": "O4x40EexJbNUnDzwf5iY8rzcUTz5gMnq", "roomName": "testing"}
    return render(request, "join.html", context)


def create_video_room(request):
    # Create a unique room name for the video call
    room_name = f"consult_{uuid.uuid4}"
    identity = str(uuid.uuid4)
    # 'O4x40EexJbNUnDzwf5iY8rzcUTz5gMnq'

    # Generate a Twilio access token
    # token = AccessToken(account_sid = "AC70ea0564259686e89e4a1c58f3bb98e2", token = "dcd4a31c42d209c6df17fc3ebdf539fd", identity = identity)
    token = AccessToken(
        "AC70ea0564259686e89e4a1c58f3bb98e2",  # ACCOUNT_SID
        "dcd4a31c42d209c6df17fc3ebdf539fd",  # AUTH_TOKEN
        identity,
        nbf="",
        valid_until="",
    )
    token.add_grant(VideoGrant(room=room_name))

    matting_url = f"http://127.0.0.1:9000/doctor/join_call?identity={identity}&roomName={room_name}"
    # Return the token as a JSON response
    return JsonResponse({"token": token.to_jwt()})


# class ZoomMeetingView(APIView):
#     def post(self, request, format=None):
#         topic = request.data.get("topic")
#         # Format: '2023-07-26T15:00:00'
#         start_time = request.data.get("start_time")
#         # duration = request.data.get('duration')  # Duration in minutes

#         if topic and start_time:
#             headers = {
#                 "Authorization": f"Bearer {settings.ZOOM_API_TOKEN}",
#                 "Content-Type": "application/json",
#             }

#             data = {
#                 "topic": topic,
#                 "type": 2,  # Scheduled Meeting
#                 "start_time": start_time,
#                 "duration": settings.MEETING_DURATION,
#                 "timezone": "UTC",  # Adjust as needed
#             }

#             response = requests.post(
#                 "https://api.zoom.us/v2/users/me/meetings", json=data, headers=headers
#             )

#             if response.status_code == 201:
#                 meeting_data = response.json()
#                 join_url = meeting_data.get("join_url")
#                 return Response({"join_url": join_url}, status=201)
#             else:
#                 return Response(
#                     {"error": "Error creating meeting"}, status=response.status_code
#                 )
#         else:
#             return Response({"error": "Missing required data"}, status=400)
