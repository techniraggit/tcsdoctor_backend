from project_setup import *
from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings
from doctor.models import Doctors, DoctorAvailability, Appointments

# from user.models import User  # Assuming the User model is in a separate 'user' app

sel = "2023-10-10 17:00"


def home(selected_date):
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d %H:%M")

    date = date_obj.strftime("%Y-%m-%d")
    time = date_obj.strftime("%H:%M:%S")
    day = date_obj.strftime("%A")

    doctors_not_in_appointments = Doctors.objects.filter(
        Q(Q(appointments__status="completed") | Q(appointments__isnull=True))
        & Q(doctor_availability__working_days__contains=[day])
        & Q(doctor_availability__start_working_hr__lte=time)
        & Q(doctor_availability__end_working_hr__gte=time)
    )
    doctors_not_in_appointments = doctors_not_in_appointments.exclude(
        appointments__date=date_obj
    )

    high_priority_doctor = doctors_not_in_appointments.filter(priority="high")
    if high_priority_doctor:
        return list(
            high_priority_doctor.order_by("?").values("id", "priority", "user__id")
        )[0]

    medium_priority_doctor = doctors_not_in_appointments.filter(priority="medium")
    if medium_priority_doctor:
        return list(
            medium_priority_doctor.order_by("?").values("id", "priority", "user__id")
        )[0]

    low_priority_doctor = doctors_not_in_appointments.filter(priority="low")
    if low_priority_doctor:
        return list(
            low_priority_doctor.order_by("?").values("id", "priority", "user__id")
        )[0]

    return "No available doctor found"


# Assuming your User and other models are properly imported and defined in your code.

print(home(sel))
