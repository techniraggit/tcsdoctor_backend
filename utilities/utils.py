import pytz
import uuid
from datetime import datetime
import re
import random

EMAIL_REGEX = re.compile(
    r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|'
    r'(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|'
    r"(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
)

MOBILE_REGEX = r"^\d{10}$"  # validate without country code


def is_valid_phone(mobile=None):
    if mobile:
        if re.match(MOBILE_REGEX, mobile):
            return True
    return False


def is_valid_email(email=None):
    if email:
        if EMAIL_REGEX.match(email):
            return True
    return False


def is_valid_date(date, date_formate):
    try:
        datetime.strptime(date, date_formate)
        return True
    except:
        return False


def generate_otp(length: int = 6):
    """Generate a random otp code of the specified length."""
    otp = ""
    for _ in range(length):
        otp += str(random.randint(0, 9))
    return otp


def get_room_no():
    return str(uuid.uuid4()).split("-")[-1]


def time_localize(dt):
    india_timezone = pytz.timezone("Asia/Kolkata")
    kolkata_time = dt.astimezone(india_timezone)
    return kolkata_time
