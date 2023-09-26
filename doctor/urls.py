from django.urls import path
from doctor import views
from doctor import tests


urlpatterns = [
    path("time_slots", views.time_slots),
    path("create_video_room", tests.create_video_room),
    path("join_call", tests.join_call),
    path("schedule_meeting", views.schedule_meeting),
    path("reschedule_meeting", views.reschedule_meeting),
    path("appointments", views.AppointmentView.as_view()),
    path("patients", views.PatientView.as_view()),
    path("notifications", views.NotificationsView.as_view()),
]
