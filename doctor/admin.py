from django.contrib import admin
from doctor.models import *

admin.site.register(Prescriptions)
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


@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = [
        "patient_id",
        "user",
        "name",
        "phone",
        "email",
        "dob",
        "gender",
    ]
    search_fields = ["name", "phone", "email"]


@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = [
        "appointment_id",
        "patient",
        "doctor",
        "status",
        "free_meetings_count",
        "schedule_date",
        "payment_status",
        "is_join",
        "room_name",
    ]
    search_fields = ["appointment_id", "status", "is_join", "room_name"]
    list_filter = ["status", "is_join"]


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

    search_fields = ["doctor__user__id", "doctor__user__email"]



@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ["id", "start_time"]


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ["doctor", "date", "time_slot", "is_booked"]
    search_fields = ["date"]


@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = ["doctor", "leave_date", "is_sanction"]
    list_filter = ["doctor", "is_sanction"]


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ["appointment", "trans_id", "paid_amount", "pay_mode", "created"]
