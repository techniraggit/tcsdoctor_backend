from django.urls import path
from doctor import views
from doctor import twilio_controller


urlpatterns = [
    path("time_slots", views.time_slots),
    path("create_video_room", twilio_controller.create_video_room),
    path("schedule_meeting", views.schedule_meeting),
    path("reschedule_meeting", views.reschedule_meeting),
    path("cancel_meeting", views.cancel_meeting),
    path("appointments", views.AppointmentView.as_view()),
    path("patients", views.PatientView.as_view()),
    path("notifications", views.NotificationsView.as_view()),
    path("profile", views.ProfileView.as_view()),
    path("consult", views.ConsultView.as_view()),
]
