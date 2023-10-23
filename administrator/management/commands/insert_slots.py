from django.core.management.base import BaseCommand
from doctor.models import TimeSlot
import os
from datetime import datetime, timedelta

start_time = datetime.strptime("00:00", "%H:%M")
end_time = datetime.strptime("23:59", "%H:%M")
interval = timedelta(minutes=15)

LOCK_FILE = ".lock"


class Command(BaseCommand):
    help = "Run a script after migrations have been applied successfully to add time slots in db"

    def handle(self, *args, **options):
        if not os.path.exists(LOCK_FILE):
            data_list = []
            current_time = start_time
            while current_time <= end_time:
                time_ = current_time.strftime("%H:%M")
                data_list.append(TimeSlot(start_time=time_))
                current_time += interval

            TimeSlot.objects.bulk_create(data_list)
        open(LOCK_FILE, "w").write(
            "✧˚·̩̩̥͙˚̩̥̩̥·̩̩̥͙✧·̩̩̥͙˚̩̥̩̥˚·̩̩̥͙✧ 𝒯𝒽𝒾𝓈 𝒻𝒾𝓁𝑒 𝒾𝓈 𝓁𝑜𝒸𝓀𝑒𝒹 ·̩̩̥͙✧·̩̩̥͙˚̩̥̩̥˚·̩̩̥͙✧"
        )
        self.stdout.write(self.style.SUCCESS("Script executed successfully"))
