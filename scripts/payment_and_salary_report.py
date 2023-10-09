from project_setup import *
from django.db.models import Count, DateTimeField, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from doctor.models import Appointments

# Get the current year and create a list of months
current_year = timezone.now().year
months = [timezone.datetime(current_year, month, 1) for month in range(1, 13)]

from django.db.models import Count, DateTimeField
from django.db.models.functions import TruncMonth
from django.db.models import Q

# Get all doctor appointments grouped by months
doctor_appointments = Appointments.objects.annotate(
    month=TruncMonth('schedule_date')
).values('month', 'doctor__user__first_name').annotate(appointment_count=Count('id')).order_by('month')

for appointment in doctor_appointments:
    print(f"Doctor: {appointment['doctor__user__first_name']}")
    print(f"Month: {appointment['month'].strftime('%B %Y')}")
    print(f"Appointment Count: {appointment['appointment_count']}")
