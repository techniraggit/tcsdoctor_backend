from django.db import models
from accounts.models import User
from django.core.validators import FileExtensionValidator
from core.mixins import DateTimeFieldMixin

# Create your models here.


class PushNotification(DateTimeFieldMixin):
    NOTIFICATION_TYPE_CHOICE = (
        ("schedule", "Schedule"),
        ("reschedule", "Reschedule"),
        ("promotional", "Promotional"),
        ("system", "System"),
    )
    users = models.ManyToManyField(User, through="UserPushNotification")
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30, choices=NOTIFICATION_TYPE_CHOICE, null=True, blank=True
    )

    class Meta:
        db_table = "push_notification"

    def __str__(self):
        return str(self.title)


class UserPushNotification(DateTimeFieldMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(PushNotification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "user_push_notification"

    def __str__(self):
        return f"{self.user} - {self.notification.title}"
