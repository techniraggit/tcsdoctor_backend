from project_setup import *
from doctor.models import DoctorAvailability, DoctorLeave, TimeSlot, Availability
from datetime import datetime, timedelta
DATE_FORMATE = "%Y/%m/%d"

def UpdateSlot(day=7):
    day = (datetime.now() + timedelta(days=day)).strftime(DATE_FORMATE)
    date_obj = datetime.strptime(day, DATE_FORMATE)
    doctors_on_leave = DoctorLeave.objects.filter(leave_date=date_obj, is_sanction=True).values_list("doctor__user__id", flat=True)
    day_name = date_obj.strftime("%A")
    doctors = DoctorAvailability.objects.filter(working_days__contains = [day_name]).select_related("doctor").exclude(doctor__user__id__in = doctors_on_leave)


    for doctor in doctors:
        slots = TimeSlot.objects.filter(start_time__range=(doctor.start_working_hr, doctor.end_working_hr))
        for slot in slots:
            try:
                Availability.objects.create(
                    doctor = doctor.doctor,
                    date = date_obj.date(),
                    time_slot = slot
                )
            except:
                pass

def GetSlot(date):
    avail = Availability.objects.filter(date=date, is_booked=False).values("time_slot__start_time")
    print(avail.count())
    return avail


def DeleteSlot():
    yesterday = (datetime.today()) - timedelta(days=1)
    avail = Availability.objects.filter(date=yesterday).delete()
    print(avail)


# GetSlot("2023-10-20")
UpdateSlot(3)
# DeleteSlot()

