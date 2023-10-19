from project_setup import *
from utilities import TIME_SLOTS
from doctor.models import TimeSlot
import os

LOCK_FILE = ".lock"

if os.path.exists(LOCK_FILE):
    exit(1)
open(LOCK_FILE, "w").write(
    "✧˚·̩̩̥͙˚̩̥̩̥·̩̩̥͙✧·̩̩̥͙˚̩̥̩̥˚·̩̩̥͙✧ 𝒯𝒽𝒾𝓈 𝒻𝒾𝓁𝑒 𝒾𝓈 𝓁𝑜𝒸𝓀𝑒𝒹 ·̩̩̥͙✧·̩̩̥͙˚̩̥̩̥˚·̩̩̥͙✧"
)

data_list = []
for time in TIME_SLOTS.values():
    data_list.append(TimeSlot(start_time=time))

TimeSlot.objects.bulk_create(data_list)
