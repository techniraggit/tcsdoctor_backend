# import requests
# import jwt
# import time

# def generate_jwt_token():
#     # Replace with your actual client ID and client secret
#     CLIENT_ID = "dKC9oEqnTbVsDXQSDMtQ"
#     CLIENT_SECRET = "mHsDnF8wHuaoBvt0ipmVo8ndfcNr0aQR"

#     # Build the JWT token payload
#     token_payload = {
#         "iss": CLIENT_ID,
#         "exp": int(time.time()) + 3600  # Expiration time (1 hour)
#     }

#     # Generate the JWT token using the client secret
#     token = jwt.encode(token_payload, CLIENT_SECRET, algorithm='HS256')

#     return token

# def create_zoom_meeting():
#     # Generate the JWT token
#     access_token = generate_jwt_token()

#     # Zoom API endpoint for creating a meeting
#     api_url = "https://api.zoom.us/v2/users/me/meetings"

#     # Set headers with the access token
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }

#     # Request payload to create a meeting
#     payload = {
#         "topic": "My Zoom Meeting",
#         "type": 1  # Scheduled meeting
#         # Add more meeting details as needed
#     }

#     data = {
#                 "topic": "topic",
#                 "type": 2,  # Scheduled Meeting
#                 "start_time": "2023-07-26T15:00:00", # Format: '2023-07-26T15:00:00'
#                 "duration": "15",
#                 "timezone": "UTC"  # Adjust as needed
#             }

#     # Make a POST request to create the meeting
#     response = requests.post(api_url, json=payload, headers=headers)
#     print(response.text)

#     if response.status_code == 201:
#         meeting_data = response.json()
#         return meeting_data
#     else:
#         print("Failed to create meeting")
#         return None

# # Call the function to create a Zoom meeting
# meeting_info = create_zoom_meeting()
# if meeting_info:
#     print("Meeting created successfully:", meeting_info)


# #--------------------------------------------------------------------------------------


# import os
# import uuid
# from twilio.rest import Client

# TWILIO_ACCOUNT_SID="AC9c00b562320674207f7afed84d9c3d7b"
# TWILIO_AUTH_TOKEN="0950c8a3ff5bfdf99aa1c51e2ba92733"

# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# unique_room_name = "guest_room_" + str(uuid.uuid4())

# room = client.video.v1.rooms.create(type='group', unique_name=unique_room_name)


# print("url ==== ", room.url)


# from core.utils import Response


# return Response(True, 'djkds', 200, "fsj", {"s":'d'}, "result")
