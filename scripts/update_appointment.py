from project_setup import *
from datetime import timedelta
from doctor.models import Appointments
from django.utils import timezone
from utilities.utils import time_localize


def update_appointments():
    fifteen_min_before_dt = time_localize(
        (timezone.now() - timedelta(minutes=15)).replace(second=0, microsecond=0)
    )
    seven_days_before_dt = time_localize(
        (timezone.now() - timedelta(days=7)).replace(second=0, microsecond=0)
    )

    Appointments.objects.filter(
        schedule_date__date=fifteen_min_before_dt.date(),
        is_attend_by_user=True,
        is_attend_by_doctor=True,
    ).exclude(status="expired").update(status="completed")

    appointments_obj = Appointments.objects.filter(
        schedule_date=seven_days_before_dt,
    ).exclude(status="expired")

    appointments_obj.filter(status="completed").update(pass_code="", room_name="")
    appointments_obj.exclude(status="completed").update(
        status="expired", pass_code="", room_name=""
    )


if __name__ == "__main__":
    update_appointments()
