from django.urls import path
from user import views

urlpatterns = [
    path("time_slots", views.time_slots),
    path("schedule_meeting", views.schedule_meeting),
    path("amount_payment", views.amount_payment),
    path("reschedule_meeting", views.reschedule_meeting),
    path("cancel_meeting", views.cancel_meeting),
    path("my_appointments", views.my_appointments),
    path("user_verification", views.user_verification),
    path("user_payment_price", views.user_payment_price),
    path("validate_call_user", views.validate_call_user),
]
