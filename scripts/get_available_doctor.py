from project_setup import *
from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings
from django.db.models import Min, Max
from doctor.models import Doctors

sel = "2023-09-28 12:00"


def home(selected_date):
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d %H:%M")

    date = date_obj.strftime("%Y-%m-%d")
    time = date_obj.strftime("%H:%M:%S")
    day = date_obj.strftime("%A")

    print("Date:", date)
    print("Time:", time)
    print("Day:", day)

    doctors_not_in_appointments = Doctors.objects.filter(
        Q(Q(appointments__status="completed") | Q(appointments__isnull=True)) &
        Q(working_days__contains=[day]) &
        Q(start_working_hr__lte=time) &
        Q(end_working_hr__gte=time)
    )

    high_priority_doctor = doctors_not_in_appointments.filter(priority='high')
    if high_priority_doctor:
        return (list(high_priority_doctor.order_by('?').values("id", "priority"))[0])
    

    medium_priority_doctor = doctors_not_in_appointments.filter(priority='medium')
    if medium_priority_doctor:
        return (list(medium_priority_doctor.order_by('?').values("id", "priority", "user__id"))[0])
    

    low_priority_doctor = doctors_not_in_appointments.filter(priority='low')
    if low_priority_doctor:
        return (list(low_priority_doctor.order_by('?').values("id", "priority"))[0])


print(home(sel))