from django.urls import path
from doctor import views
from doctor import twilio_controller


urlpatterns = [
    path("time_slots", views.time_slots),
    path("create_video_room", twilio_controller.create_video_room),
    path("schedule_meeting", views.schedule_meeting),
    path("amount_payment", views.amount_payment),
    path("reschedule_meeting", views.reschedule_meeting),
    path("cancel_meeting", views.cancel_meeting),
    path("appointments", views.AppointmentView.as_view()),
    path("patients", views.PatientView.as_view()),
    path("patient_detailed", views.PatientDetailView.as_view()),
    path("notifications", views.NotificationsView.as_view()),
    path("profile", views.ProfileView.as_view()),
    path("consult", views.ConsultView.as_view()),
    path("my_appointments", views.my_appointments),
    path("user_verification", views.user_verification),
    path("user_payment_price", views.user_payment_price),
    path("validate_call_user", views.validate_call_user),
    path("validate_call_doctor", views.ValidateCallDoctorView.as_view()),
]
