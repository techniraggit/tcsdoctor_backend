from project_setup import *
from utilities.utils import time_localize
from utilities.pigeon.service import send_email
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from doctor.models import Appointments


def update_appointments():
    current_time = datetime.now() - timedelta(minutes=15)

    appointments_obj = Appointments.objects.filter(
        schedule_date__lt=current_time,
    ).exclude(status="expired")
    completed_appointments = appointments_obj.filter(status="completed")
    incomplete_appointments = appointments_obj.exclude(status="completed")
    completed_appointments.update(meeting_link="", pass_code="", room_name="")
    incomplete_appointments.update(status="expired", pass_code="", room_name="")


def send_reminder():
    future_datetime = time_localize(
        (timezone.now() + timezone.timedelta(minutes=15)).replace(
            second=0, microsecond=0
        )
    )

    appointments = Appointments.objects.filter(
        Q(status="scheduled") | Q(status="rescheduled"),
        schedule_date=future_datetime,
        payment_status="paid",
    )

    for appointment in appointments:
        context = {
            "user_name": appointment.patient.name,
            "appointment_date": time_localize(appointment.schedule_date).date(),
            "appointment_time": time_localize(appointment.schedule_date).time(),
        }
        message = render_to_string("email/appointment_reminder.html", context)
        subject = "Reminder for upcoming Appointment"
        recipient_email = appointment.patient.email
        send_email(subject=subject, message=message, recipients=[recipient_email])


if __name__ == "__main__":
    update_appointments()
    send_reminder()
