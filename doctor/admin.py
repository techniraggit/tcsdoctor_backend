from django.contrib import admin
from doctor.models import *

# Register your models here.
# admin.site.register(Doctors)
admin.site.register(Patients)
admin.site.register(Prescriptions)
# admin.site.register(Appointments)
admin.site.register(Consultation)
admin.site.register(Feedbacks)
admin.site.register(DoctorExperience)


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = [
        "user_id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
    ]
    list_filter = ["user_id", "email", "phone_number"]
    search_fields = ["user_id", "email", "phone_number"]


@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "patient",
        "doctor",
        # "schedule_date",
        "status",
        "meeting_link",
    ]
    search_fields = ["id", "status"]


@admin.register(Doctors)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "clinic_name",
        "clinic_contact_no",
        # "start_working_hr",
        # "end_working_hr",
        "priority",
        "working_days",
        "is_active",
    ]
    list_filter = ["is_active"]
    search_fields = ["user_id", "user__email", "user__phone_number", "clinic_name"]
