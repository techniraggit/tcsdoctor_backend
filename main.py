import os
import uuid
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv("config.env")

#Twilio
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
unique_room_name = "guest_room_" + str(uuid.uuid4())

room = client.video.v1.rooms.create(type='group', unique_name=unique_room_name)


print("url ==== ", room.url)