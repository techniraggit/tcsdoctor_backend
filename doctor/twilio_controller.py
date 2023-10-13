import uuid
from django.http import JsonResponse
from utilities.video.auth import get_access_token

def create_video_room(request):
    room_name = f"consult_{uuid.uuid4()}"
    identity = str(uuid.uuid4())
    token = get_access_token(identity=identity, room_name=room_name)

    return JsonResponse({"token": token, "room_name": room_name})
