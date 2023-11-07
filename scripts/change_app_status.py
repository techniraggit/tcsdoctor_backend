from project_setup import *
from django.utils import timezone
from datetime import datetime, timedelta
from doctor.models import Appointments

def update_appointments():
    current_time = (datetime.now() - timedelta(minutes=15))

    appointments_obj = Appointments.objects.filter(
        schedule_date__lt=current_time,
    ).exclude(status="expired")
    completed_appointments = appointments_obj.filter(status="completed")
    incomplete_appointments = appointments_obj.exclude(status="completed")
    completed_appointments.update(meeting_link="", pass_code="", room_name="")
    incomplete_appointments.update(status="expired", pass_code="", room_name="")

if __name__ == '__main__':
    update_appointments()
