from django.core.management.base import BaseCommand
from scripts.update_slots import UpdateSlot, DeleteSlot


class Command(BaseCommand):
    help = "Update time slots for a given date"

    def add_arguments(self, parser):
        parser.add_argument("day", type=str, help="number of day")

    def handle(self, *args, **options):
        try:
            arg_1 = int(options["day"])
            response = UpdateSlot(arg_1)
            DeleteSlot()
            self.stdout.write(self.style.SUCCESS(f"Slots have been successfully updated for {response}."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
