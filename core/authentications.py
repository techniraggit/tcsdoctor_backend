from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError


class UniqueTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = self.get_token_from_request(request)

        if token is None:
            raise AuthenticationFailed("Authentication credentials were not provided.")

        if cache.get(token):
            raise AuthenticationFailed("Token is already in use.")

        try:
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

        except ExpiredSignatureError:
            raise AuthenticationFailed("Token is invalid or expired")

        try:
            user_model = get_user_model()
            user = user_model.objects.get(pk=payload.get("user_id"))

        except user_model.DoesNotExist:
            raise AuthenticationFailed("No such user")

        return (user, token)

    def get_token_from_request(self, request):
        try:
            header = request.META.get("HTTP_AUTHORIZATION", "").split()[-1]
            return header
        except IndexError:
            return None
