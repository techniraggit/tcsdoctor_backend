from datetime import datetime, timedelta
from django.core.cache import cache
from project_setup import *
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.db.models import Min, Max
from datetime import datetime, timedelta, time
from doctor.models import Doctors, Appointments
from datetime import datetime
from utilities import TIME_SLOTS

TIME_FORMATE = "%Y/%m/%d"


def slots(selected_date):
    date_obj = datetime.strptime(selected_date, TIME_FORMATE)
    day = date_obj.strftime("%A")
    date = date_obj.date()
    current_date = datetime.now().date()
    current_time = datetime.now().time().replace(microsecond=0)

    doctors = Doctors.objects.filter(
        Q(Q(appointments__status="completed") | Q(appointments__isnull=True))
        & Q(doctor_availability__working_days__contains=[day])
    ).distinct()

    if not doctors:
        return [], []
    doctor_ids = list(doctors.values_list("user__id", flat=True))

    day_time_distance = doctors.aggregate(
        min_time=Min("doctor_availability__start_working_hr"),
        max_time=Max("doctor_availability__end_working_hr"),
    )

    day_start_time = day_time_distance.get("min_time")
    day_end_time = day_time_distance.get("max_time")

    if current_date == date:
        day_start_time = current_time

    start_time = day_start_time
    end_time = day_end_time

    # Define the start and end times for the working day
    start_time = time(start_time.hour, start_time.minute)
    end_time = time(end_time.hour, end_time.minute)

    # Generate available time slots within the working hours
    current_time = datetime.combine(date_obj, start_time).time().strftime("%H:%M")
    end_of_day = datetime.combine(date_obj, end_time).time().strftime("%H:%M")

    start_time = current_time  # "15:15"
    end_time = end_of_day  # "19:14"

    # Convert start and end times to a comparable integer value
    start_minutes = int(start_time[:2]) * 60 + int(start_time[3:])
    end_minutes = int(end_time[:2]) * 60 + int(end_time[3:])

    # Filter the slots based on the specified time range
    appointments = Appointments.objects.all()
    filtered_slots = {}
    key_ids = []
    for key, value in TIME_SLOTS.items():
        if start_minutes < int(value[:2]) * 60 + int(value[3:]) < end_minutes:
            filtered_slots[key] = value
            key_ids.append(key)
    return key_ids, doctor_ids


def get_timeout(date):
    current_date = datetime.now()
    future_date = datetime.strptime(date, TIME_FORMATE)
    time_difference = ((future_date + timedelta(days=1)) - current_date).total_seconds()
    return time_difference


def next_dates(days=7):
    date_list = [
        (datetime.now() + timedelta(days=day)).strftime(TIME_FORMATE)
        for day in range(days)
    ]
    return date_list


def set_cache_data(date, keys, doctors):
    data_dict = {}
    for key in keys:
        data_dict[key] = doctors
        cache.set(date, data_dict, timeout=get_timeout(date))


def UpdateAppointment():
    dates = next_dates()
    for date in dates:
        keys, doctors = slots(date)
        set_cache_data(date, keys, doctors)


def FindAvailableSlots(date):
    data = cache.get(date)
    result_dict = {}

    for key in data.keys():
        if key in TIME_SLOTS:
            result_dict[key] = TIME_SLOTS.get(key)
    return result_dict


def FindAvailableDoctor(date, time):
    found_key = None

    for key, value in TIME_SLOTS.items():
        if value == time:
            found_key = key
            break
    data = {found_key: (cache.get(date)).get(found_key)}
    return data


def UpdateSlot(date, slot_dict, id):
    key = list(slot_dict.keys())[0]

    if key in slot_dict:
        slot_dict[key] = [x for x in slot_dict[key] if x != id]

    cache.set(date, slot_dict)


if __name__ == "__main__":
    date_ = "2023/10/25"
    time_ = "22:00"
    slot_ = {88: [2, 3, 4, 5]}
    id_ = 4
    # UpdateAppointment()
    # print(FindAvailableSlots(date_))
    drs = FindAvailableDoctor(date_, time_)
    print("drs === ", drs)
    # dr_id = Doctors.objects.filter(user__id__in=list(drs.values())[0]).order_by("priority").first().user.id
    # print(dr_id)
    # UpdateSlot(date_, drs, dr_id)
