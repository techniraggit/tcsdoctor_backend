from datetime import datetime, timedelta, time
from doctor.models import Doctors, Appointments
from django.db.models import Q, Min, Max
from django.conf import settings


def get_available_time_slots(selected_date):
    """get available time slots for the selected date"""
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    day = date_obj.strftime("%A")

    # Get the list of doctors who meet the criteria, as you did in your previous function
    doctors_not_in_appointments = Doctors.objects.filter(
        Q(Q(appointments__status="completed") | Q(appointments__isnull=True))
        & Q(working_days__contains=[day])
    )

    aggregated_data = doctors_not_in_appointments.aggregate(
        min_start_time=Min("start_working_hr"), max_end_time=Max("end_working_hr")
    )

    start_time = aggregated_data["min_start_time"]
    end_time = aggregated_data["max_end_time"]

    # Assuming your time slot duration is 15 minutes
    slot_duration = timedelta(minutes=settings.MEETING_DURATION)

    # Define the start and end times for the working day
    start_time = time(9, 0)  # Replace with the desired start time
    end_time = time(22, 0)  # Replace with the desired end time

    # Generate available time slots within the working hours
    current_time = datetime.combine(date_obj, start_time)
    end_of_day = datetime.combine(date_obj, end_time)

    available_time_slots = []

    while current_time + slot_duration <= end_of_day:
        # Check if the current time slot is available
        if not doctors_not_in_appointments.filter(
            Q(start_working_hr__lte=current_time.time())
            & Q(end_working_hr__gte=(current_time + slot_duration).time())
        ).exists():
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
        & Q(working_days__contains=[day])
        & Q(start_working_hr__lte=time)
        & Q(end_working_hr__gte=time)
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
