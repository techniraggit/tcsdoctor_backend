from django.urls import path
from accounts.views import (
    AdminLoginView,
    SendLoginOTPView,
    ValidateLoginOTPView,
    Logout,
)

urlpatterns = [
    path("login", AdminLoginView.as_view()),
    path("send-login-otp", SendLoginOTPView.as_view()),
    path("validate-login-otp", ValidateLoginOTPView.as_view()),
    path("logout", Logout.as_view()),
]
