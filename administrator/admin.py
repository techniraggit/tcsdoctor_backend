from django.contrib import admin
from administrator.models import *

# Register your models here.
@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "message", "notification_type"]

@admin.register(UserPushNotification)
class UserPushNotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "notification", "is_read"]

@admin.register(UserPaymentPrice)
class UserPaymentPriceAdmin(admin.ModelAdmin):
    list_display = ["id", "price", "created_by", "created"]
    search_fields = ["price", "id"]