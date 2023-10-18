from datetime import datetime, timedelta, time
from doctor.models import Doctors, Appointments
from django.db.models import Q, Min, Max
from django.conf import settings


def get_available_time_slots(selected_date):
    """get available time slots for the selected date"""
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    day = date_obj.strftime("%A")
    date = date_obj.date()
    current_date = datetime.now().date()
    current_time = datetime.now().time().replace(microsecond=0)

    doctors = Doctors.objects.filter(
            Q(Q(appointments__status="completed") | Q(appointments__isnull=True)) &
            Q(doctor_availability__working_days__contains=[day])).distinct()

    doctor_ids = list(doctors.values_list("user__id", flat=True))

    day_time_distance = doctors.aggregate(min_time=Min("doctor_availability__start_working_hr"), max_time=Max("doctor_availability__end_working_hr"))

    day_start_time = day_time_distance.get("min_time")
    day_end_time = day_time_distance.get("max_time")

    if current_date == date:
        day_start_time = current_time

    start_time = day_start_time
    end_time = day_end_time

    # Assuming your time slot duration is 15 minutes
    slot_duration = timedelta(minutes=settings.SLOT_DURATION)

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


def get_available_doctor(selected_date):
    """get available doctor on base selected date and time"""
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d %H:%M")

    date = date_obj.strftime("%Y-%m-%d")
    time = date_obj.strftime("%H:%M:%S")
    day = date_obj.strftime("%A")

    print("Date:", date)
    print("Time:", time)
    print("Day:", day)

    doctors_not_in_appointments = Doctors.objects.filter(
        Q(Q(appointments__status="completed") | Q(appointments__isnull=True))
        & Q(doctor_availability__working_days__contains=[day])
        & Q(doctor_availability__start_working_hr__lte=time)
        & Q(doctor_availability__end_working_hr__gte=time)
    )

    high_priority_doctor = doctors_not_in_appointments.filter(priority="high")
    if high_priority_doctor:
        return list(high_priority_doctor.order_by("?").values("id", "priority"))[0]

    medium_priority_doctor = doctors_not_in_appointments.filter(priority="medium")
    if medium_priority_doctor:
        return list(medium_priority_doctor.order_by("?").values("id", "priority"))[0]

    low_priority_doctor = doctors_not_in_appointments.filter(priority="low")
    if low_priority_doctor:
        return list(low_priority_doctor.order_by("?").values("id", "priority"))[0]
