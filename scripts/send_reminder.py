from project_setup import *
from utilities.utils import time_localize
from utilities.pigeon.service import send_email
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils import timezone
from doctor.models import Appointments

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
        send_email(subject=subject, body=message, recipients=[recipient_email])


if __name__ == "__main__":
    send_reminder()