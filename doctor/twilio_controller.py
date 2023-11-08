import uuid
from django.http import JsonResponse
from utilities.video.auth import get_access_token


def create_video_room(request):
    room_name = request.GET.get("room_name")
    if not room_name:
        return JsonResponse({"status": False, "message": "Room name not found"})

    identity = str(uuid.uuid4())
    status, token = get_access_token(identity=identity, room_name=room_name)
    if status:
        return JsonResponse(
            {"status": status, "token": token, "room_name": room_name}, status=200
        )
    return JsonResponse(
        {"status": status, "message": "Token generation failed"}, status=500
    )
