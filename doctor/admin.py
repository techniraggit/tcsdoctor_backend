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
        "appointment_id",
        "patient",
        "doctor",
        "status",
        "meeting_link",
        "no_cost_consult",
    ]
    search_fields = ["appointment_id", "status"]
    list_filter = ["status"]



@admin.register(Doctors)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "clinic_name",
        "clinic_contact_no",
        "priority",
        "is_active",
    ]
    list_filter = ["is_active"]
    search_fields = ["user_id", "user__email", "user__phone_number", "clinic_name"]

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = [
        "doctor",
        "start_working_hr",
        "end_working_hr",
        "working_days",
    ]

    search_fields = ["doctor__user__id"]


@admin.register(NotePad)
class NotePadAdmin(admin.ModelAdmin):
    list_display = "room_name", "notepad"

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ["id", "start_time"]


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ["doctor", "date", "time_slot", "is_available", "is_booked"]
