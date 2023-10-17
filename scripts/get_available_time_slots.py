from project_setup import *
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.db.models import Min, Max
from datetime import datetime, timedelta, time
from doctor.models import Doctors, Appointments
from datetime import datetime

# current_datetime = timezone.now()
selected_date = "2023-10-16"

def home(selected_date):
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    day = date_obj.strftime("%A")
    date = date_obj.date()
    current_date = datetime.now().date()
    current_time = datetime.now().time().replace(microsecond=0)

    doctors = Doctors.objects.filter(
            Q(Q(appointments__status="completed") | Q(appointments__isnull=True)) &
            Q(doctor_availability__working_days__contains=[day])).distinct()

    if not doctors:
        return "No doctor available for this day"


    doctor_ids = list(doctors.values_list("user__id", flat=True))

    day_time_distance = doctors.aggregate(min_time=Min("doctor_availability__start_working_hr"), max_time=Max("doctor_availability__end_working_hr"))

    day_start_time = day_time_distance.get("min_time")
    day_end_time = day_time_distance.get("max_time")

    if current_date == date:
        day_start_time = current_time

    start_time = day_start_time
    end_time = day_end_time

    # Assuming your time slot duration is 15 minutes
    slot_duration = timedelta(minutes=settings.MEETING_DURATION)

    # Define the start and end times for the working day
    start_time = time(
        start_time.hour, start_time.minute
    )  # Replace with the desired start time
    end_time = time(end_time.hour, end_time.minute)  # Replace with the desired end time

    # Generate available time slots within the working hours
    current_time = datetime.combine(date_obj, start_time)
    end_of_day = datetime.combine(date_obj, end_time)

    available_time_slots = []

    while current_time + slot_duration <= end_of_day:

        if not doctors.filter( Q(doctor_availability__start_working_hr__gte=current_time.time()) & Q(doctor_availability__end_working_hr__lte=(current_time + slot_duration).time())).exists():
            available_time_slots.append(
                {
                    "start_time": current_time.time().strftime("%H:%M"),
                    "end_time": (current_time + slot_duration).time().strftime("%H:%M"),
                }
            )

        current_time += slot_duration
    return available_time_slots


print(home(selected_date))