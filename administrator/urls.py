from django.urls import path
from administrator import views


urlpatterns = [
    path("dashboard", views.DashboardView.as_view()),
    path("doctor", views.DoctorView.as_view()),
    path("patient", views.PatientView.as_view()),
    path("appointment", views.AppointmentView.as_view()),
    path("get_push_notification_types", views.get_push_notification_types),
    path("get_all_doctors_email", views.get_all_doctors_email),
    path("push-notification", views.PushNotificationView.as_view()),
    path("download-report", views.DownloadReportView.as_view()),
    path("appointment-list", views.AppointmentListView.as_view()),
    path("slots_information", views.SlotInfoView.as_view()),
]
