from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from utilities.pigeon.templates import LOGIN_OTP
from accounts.utils import get_tokens_for_user
from accounts.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import (  # Django Auth
    authenticate,
)
from django.db.models import Q
from utilities.pigeon.service import send_email, send_sms
from django.template.loader import render_to_string

# Create your views here.


class AdminLoginView(APIView):
    def post(self, request):
        email = request.data.get("email", "None").lower()
        password = request.data.get("password")

        if not all([email, password]):
            return Response(
                {"status": False, "message": "required fields are missing"}, 400
            )

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "You're not a valid user"}, 400
            )

        auth_user = authenticate(username=email, password=password)

        if auth_user:
            if auth_user.is_superuser:
                access_token, refresh_token = get_tokens_for_user(auth_user)
                user_type = "admin" if auth_user.is_superuser else "doctor"

                return Response(
                    {
                        "status": True,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user_type": user_type,
                        "first_name": auth_user.first_name,
                        "last_name": auth_user.last_name,
                    },
                    200,
                )
            return Response(
                {
                    "status": False,
                    "message": "Access denied. You do not have the necessary permissions to access this resource. Please contact the administrator for assistance.",
                },
                403,
            )

        return Response(
            {"status": False, "message": "Check your email or password and try again."},
            400,
        )


class SendLoginOTPView(APIView):
    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response({"status": False, "message": "Username required"}, 400)

        user_get = User.objects.filter(
            Q(email=username.lower()) | Q(phone_number=username)
        ).first()

        if user_get:
            user_get.get_otp()
            if user_get.email == username:
                context = {
                    "name": user_get.first_name,
                    "otp": user_get.otp,
                }
                subject = "Your OTP for Secure Login"
                body = render_to_string("email/send_otp.html", context=context)
                send_email(subject, body, [user_get.email])
                return Response(
                    {"status": True, "message": f"Otp sent to {user_get.email}"}
                )

            else:
                send_sms(
                    user_get.phone_number,
                    LOGIN_OTP.format(first_name=user_get.first_name, otp=user_get.otp),
                )
                return Response(
                    {"status": True, "message": f"Otp sent to {user_get.phone_number}"}
                )
        return Response(
            {
                "status": False,
                "message": "You are not recognized as a valid user. Please ensure you are using the correct credentials or register as a new user.",
            },
            status=400,
        )


class ValidateLoginOTPView(APIView):
    def post(self, request):
        username = request.data.get("username", "").lower()
        otp = request.data.get("otp")
        if not all([username, otp]):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )

        user_get = User.objects.filter(
            Q(email=username) | Q(phone_number=username)
        ).first()

        if user_get:
            otp_verification = user_get.auth_otp(otp)
            if otp_verification == "1":
                if user_get.is_staff:
                    access_token, refresh_token = get_tokens_for_user(user_get)
                    user_type = "admin" if user_get.is_superuser else "doctor"

                    return Response(
                        {
                            "status": True,
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "user_type": user_type,
                            "first_name": user_get.first_name,
                            "last_name": user_get.last_name,
                        },
                        200,
                    )
                return Response(
                    {
                        "status": False,
                        "message": "Access Denied. You do not have the necessary permissions to access this content. Please contact the administrator for assistance.",
                    },
                    403,
                )
            elif otp_verification == "0":
                return Response(
                    {
                        "status": False,
                        "message": "Expired otp",
                    },
                    400,
                )
            else:
                return Response(
                    {
                        "status": False,
                        "message": " Invalid OTP. Please provide a valid one.",
                    },
                    400,
                )
        return Response(
            {
                "status": False,
                "message": "You are not recognized as a valid user. Please ensure you are using the correct credentials or register as a new user.",
            },
            status=400,
        )


class Logout(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return Response(
            {"status": True, "message": "You have been logged out successfully"}, 200
        )
