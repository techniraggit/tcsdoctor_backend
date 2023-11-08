from django.urls import path
from doctor import views
from doctor import twilio_controller


urlpatterns = [
    path("create_video_room", twilio_controller.create_video_room),
    path("appointments", views.AppointmentView.as_view()),
    path("patients", views.PatientView.as_view()),
    path("patient_detailed", views.PatientDetailView.as_view()),
    path("notifications", views.NotificationsView.as_view()),
    path("profile", views.ProfileView.as_view()),
    path("consult", views.ConsultView.as_view()),
    path("validate_call_doctor", views.ValidateCallDoctorView.as_view()),
]
