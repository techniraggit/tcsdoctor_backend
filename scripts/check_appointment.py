from project_setup import *
from django.utils import timezone
from doctor.models import Appointments


def update_appointments():
    seven_days_ago = timezone.now() - timezone.timedelta(days=6)

    appointments_to_update = Appointments.objects.filter(
        is_free=True, initial_schedule_date__lte=seven_days_ago
    )
    print(appointments_to_update)

    appointments_to_update.update(is_free=False)


if __name__ == "__main__":
    update_appointments()
