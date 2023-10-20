from project_setup import *
from doctor.models import DoctorAvailability, DoctorLeave
from datetime import datetime, timedelta
DATE_FORMATE = "%Y/%m/%d"

# doctors = DoctorAvailability.objects.all().select_related("doctor")
# for doctor in doctors:
#     print(doctor, doctor.start_working_hr, doctor.end_working_hr, doctor.working_days)

def next_dates(days=7):
    date_list = [
        (datetime.now() + timedelta(days=day)).strftime(DATE_FORMATE)
        for day in range(days)
    ]
    return date_list

days = next_dates()
for day in days:
    date_obj = datetime.strptime(day, DATE_FORMATE)
    doctors_on_leave = DoctorLeave.objects.filter(leave_date=date_obj, is_sanction=True).values_list("doctor__user__id", flat=True)
    day_name = date_obj.strftime("%A")
    doctors = DoctorAvailability.objects.filter(working_days__contains = [day_name]).select_related("doctor").exclude(doctor__user__id__in = doctors_on_leave)
    print(day, doctors)


(datetime.now() + timedelta(days=7)).strftime(DATE_FORMATE)