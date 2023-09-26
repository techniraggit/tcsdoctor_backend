import os
from django.http import JsonResponse
from functools import wraps
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.permissions import IsAdminOnly, IsDoctorOnly
import pretty_errors


def doctor_required(func):
    decorated_func = authentication_classes([JWTAuthentication])(func)
    decorated_func = permission_classes([IsAuthenticated, IsDoctorOnly])(func)
    return decorated_func


def admin_required(func):
    decorated_func = authentication_classes([JWTAuthentication])(func)
    decorated_func = permission_classes([IsAuthenticated, IsAdminOnly])(func)
    return decorated_func


def token_required(func):
    @wraps(func)
    def _wrapped_view(request, *args, **kwargs):
        STATIC_TOKEN = os.getenv("STATIC_TOKEN")
        request_token = request.headers.get("Authorization")
        if not request_token:
            return JsonResponse(
                {"message": "Authentication credentials were not provided."}, status=401
            )

        if request_token != f"Token {STATIC_TOKEN}":
            return JsonResponse(
                {"message": "Invalid or missing authentication token"}, status=401
            )

        return func(request, *args, **kwargs)

    return _wrapped_view
