from pathlib import Path
import sys
import subprocess


python_env_path = sys.executable
path_base = str(Path(__file__).parent.parent.parent.parent)

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Add a job to a cron scheduler."

    def handle(self, *args, **options):
        """code to be here"""
        try:
            jobs_list = []
            for job in settings.CRON_JOBS:
                script_path = str(job.split(",")[1]).strip()
                jobs_list.append(
                    f"{job.split(',')[0]} {python_env_path} {path_base}/{script_path}"
                )
            TASKS = "\n".join(jobs_list) + "\n"

            # Save the new crontab code to a temporary file
            temp_file = "/tmp/new_crontab"
            with open(temp_file, "w") as file:
                file.write(TASKS)

            # Load the new crontab code using the 'crontab' command
            command = f"crontab {temp_file}"
            subprocess.call(command, shell=True)

            # Remove the temporary file
            subprocess.call(f"rm {temp_file}", shell=True)
            self.stdout.write(self.style.SUCCESS("cron added successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
