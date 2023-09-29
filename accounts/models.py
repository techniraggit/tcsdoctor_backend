from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from accounts.managers import UserManager
from core.mixins import DateTimeFieldMixin
from utilities.utils import generate_otp
from django.core.cache import cache


# Create your models here.
class User(AbstractUser, DateTimeFieldMixin):
    """Model to manage Doctor and Admin"""

    profile_image = models.FileField(
        upload_to="user/profile_images",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(["png", "jpg", "jpeg", "svg"])],
    )
    email = models.EmailField("Email address", unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    token = models.TextField(null=True, blank=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.id}"

    def get_otp(self):
        self.otp = generate_otp()
        cache.set(f"{self.id}{self.otp}", self.otp, 60 * 5)
        self.save()
        return True

    def auth_otp(self, otp):
        if self.otp == otp:
            if cache.get(f"{self.id}{otp}"):
                self.otp = None
                self.save()
                return "1"
            return "0"
        return ""
