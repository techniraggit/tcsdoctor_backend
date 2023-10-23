# Project Setup in script
from pathlib import Path
import sys
import os
import django
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = os.path.join(BASE_DIR, "tcs_backend")

load_dotenv(f"{PROJECT_DIR}/config.env")

sys.path.append(PROJECT_DIR)
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", f"Project.settings.{os.environ.get('ENV')}"
)
django.setup()
