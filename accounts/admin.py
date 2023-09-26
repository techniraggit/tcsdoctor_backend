from django.contrib import admin
from accounts.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "email", "phone_number", "is_superuser"]
    list_filter = ["is_superuser"]
    search_fields = ["id", "email", "phone_number"]
