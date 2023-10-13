from project_setup import *
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.db.models import Min, Max
from datetime import datetime, timedelta, time
from doctor.models import Doctors, Appointments
from datetime import datetime


# current_datetime = timezone.now()
selected_date = "2023-10-12"
# selected_date = "2023-09-27 01:58"

def home(selected_date):
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    day = date_obj.strftime("%A")
    date = date_obj.date()
    current_date = datetime.now().date()
    current_time = datetime.now().time().replace(microsecond=0)

    doctors = Doctors.objects.filter(
            Q(Q(appointments__status="completed") | Q(appointments__isnull=True)) &
            Q(working_days__contains=[day])).distinct()

    doctor_ids = list(doctors.values_list("user__id", flat=True))

    day_time_distance = doctors.aggregate(min_time=Min("start_working_hr"), max_time=Max("end_working_hr"))

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
    current_time = datetime.combine(date_obj, start_time).time().strftime("%H:%M")
    end_of_day = datetime.combine(date_obj, end_time).time().strftime("%H:%M")

    from utilities import TIME_SLOTS

    now_time = datetime.now().time().strftime("%H:%M")

    start_time = "15:15"
    start_time = current_time
    end_time = "19:14"
    end_time = end_of_day

    # Convert start and end times to a comparable integer value
    start_minutes = int(start_time[:2]) * 60 + int(start_time[3:])
    end_minutes = int(end_time[:2]) * 60 + int(end_time[3:])

    # Filter the slots based on the specified time range
    appointments = Appointments.objects.all()
    filtered_slots = {}
    for key, value in TIME_SLOTS.items():
        if start_minutes < int(value[:2]) * 60 + int(value[3:]) < end_minutes:
            filtered_slots[key] = value
            filtered_slots["is_avail"] = appointments.filter(slot_key=key, schedule_date__date=date, doctor__user__id__in=doctors.values_list("user__id", flat=True)).exists()


