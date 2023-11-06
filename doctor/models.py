import os
from utilities.pigeon.service import send_sms
from administrator.models import PushNotification, UserPushNotification
from django.conf import settings
from utilities.pigeon.templates import (
    APPOINTMENT_RESCHEDULE_PATIENT,
    APPOINTMENT_BOOK_PATIENT,
    APPOINTMENT_CANCEL_PATIENT,
    APPOINTMENT_REMINDER_MESSAGE,
    APPOINTMENT_REMINDER_TITLE,
)
import uuid
from datetime import date
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    FileExtensionValidator,
)
from django.db import models
from accounts.models import User
from core.mixins import DateTimeFieldMixin
from django.contrib.postgres.fields import ArrayField

# Create your models here.
priority_choices = (
    ("high", "High"),
    ("medium", "Medium"),
    ("low", "Low"),
)
from utilities.utils import generate_otp

class Doctors(DateTimeFieldMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=50)
    medical_license = models.FileField(
        upload_to="doctor/medical_license",
        null=True,
        blank=True,
        # validators=[FileExtensionValidator(["png", "jpg", "jpeg", "svg"])],
    )

    education = models.CharField(max_length=50)
    clinic_name = models.CharField(max_length=50)
    clinic_address = models.TextField()
    clinic_contact_no = models.CharField(max_length=15, null=True, blank=True)

    priority = models.CharField(max_length=20, choices=priority_choices)

    summary = models.TextField(null=True, blank=True)
    appointment_charges = models.FloatField(null=True, blank=True)
    salary = models.FloatField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "doctors"

    def __str__(self) -> str:
        return self.user.email


class DoctorAvailability(DateTimeFieldMixin):
    doctor = models.ForeignKey(
        Doctors, on_delete=models.CASCADE, related_name="doctor_availability"
    )
    start_working_hr = models.TimeField()
    end_working_hr = models.TimeField()
    working_days = ArrayField(models.TextField())

    class Meta:
        db_table = "doctor_availability"

    def __str__(self) -> str:
        return self.doctor.user.email


class DoctorLeave(DateTimeFieldMixin):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    leave_date = models.DateField()
    is_sanction = models.BooleanField(default=False)

    class Meta:
        db_table = "doctor_leave"

    def __str__(self):
        return self.doctor.user.email


class Users(DateTimeFieldMixin):
    """Model to manage Users who will come from eyemyeye as patient"""

    user_id = models.CharField(max_length=20, editable=False, primary_key=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return f"{self.user_id}-{self.email}"


GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
)


class Patients(DateTimeFieldMixin):
    patient_id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, null=True)
    email = models.EmailField(null=True)
    dob = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)

    pre_health_issue = models.BooleanField(default=False)
    pre_health_issue_text = models.TextField(null=True, blank=True)

    treatment_undergoing = models.BooleanField(default=False)
    treatment_undergoing_text = models.TextField(null=True, blank=True)

    treatment_allergies = models.BooleanField(default=False)
    treatment_allergies_text = models.TextField(null=True, blank=True)

    additional_note = models.TextField(null=True, blank=True)

    def age(self):
        if self.dob:
            today = date.today()
            return (
                today.year
                - self.dob.year
                - ((today.month, today.day) < (self.dob.month, self.dob.day))
            )
        return 0

    def __str__(self):
        return f"{self.patient_id}-{self.name}"


class Prescriptions(DateTimeFieldMixin):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)

    # Right Eye
    right_sphere = models.FloatField()
    right_cylinder = models.FloatField(default=0.0)
    right_axis = models.PositiveIntegerField(default=0)
    right_od = models.FloatField(null=True)  # Additional Bifocal power
    right_pd = models.FloatField(default=31.5)

    # Left Eye
    left_sphere = models.FloatField()
    left_cylinder = models.FloatField(default=0.0)
    left_axis = models.PositiveIntegerField(default=0)
    left_od = models.FloatField(null=True)  # Additional Bifocal power
    left_pd = models.FloatField(default=31.5)

    remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "prescriptions"


APPOINTMENT_STATUS_CHOICES = (
    ("pending", "pending"),
    ("scheduled", "scheduled"),
    ("rescheduled", "rescheduled"),
    ("completed", "completed"),
    ("cancelled", "cancelled"),
    ("free_scheduled", "free_scheduled"),
    ("unanswered_patient", "unanswered_patient"),
    ("unanswered_doctor", "unanswered_doctor"),
)

APPOINTMENT_PAYMENT_STATUS_CHOICES = (
    ("paid", "paid"),
    ("unpaid", "unpaid"),
)



class TimeSlot(models.Model):
    start_time = models.TimeField()

    class Meta:
        db_table = "time_slot"

    def __str__(self):
        return f"{self.start_time}"


class Availability(DateTimeFieldMixin):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)

    class Meta:
        db_table = "availability"
        unique_together = ("doctor", "date", "time_slot")


class Appointments(DateTimeFieldMixin):
    appointment_id = models.AutoField(primary_key=True, editable=False)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    schedule_date = models.DateTimeField()
    initial_schedule_date = models.DateTimeField()
    slot_key = models.CharField(max_length=5)
    room_name = models.CharField(max_length=50)
    free_meetings_count = models.IntegerField(default=0)
    is_join = models.BooleanField(default=False)
    is_free = models.BooleanField(default=True)
    status = models.CharField(
        max_length=50, choices=APPOINTMENT_STATUS_CHOICES, default="pending"
    )

    payment_status = models.CharField(
        max_length=50, choices=APPOINTMENT_PAYMENT_STATUS_CHOICES, default="unpaid"
    )
    is_attend_by_user = models.BooleanField(default=False)
    is_attend_by_doctor = models.BooleanField(default=False)
    pass_code = models.CharField(max_length=6)
    meeting_link = models.URLField(null=True, blank=True)
    previous_status = models.CharField(
        max_length=50, choices=APPOINTMENT_STATUS_CHOICES, default="pending"
    )

    class Meta:
        db_table = "appointments"

    def __str__(self):
        return f"{self.appointment_id}"

    def send_sms_on_status_change(self):
        message = None
        meeting_url=f"{os.environ.get('TCS_USER_FRONTEND')}{self.room_name}"
        if self.status == "scheduled":
            message = APPOINTMENT_BOOK_PATIENT.format(
                user_name=self.patient.name,
                appointment_date=self.schedule_date.date(),
                appointment_time=self.schedule_date.time(),
                pass_code=self.pass_code,
                meeting_url = meeting_url,
            )

        elif self.status == "rescheduled":
            message = APPOINTMENT_RESCHEDULE_PATIENT.format(
                user_name=self.patient.name,
                appointment_date=self.schedule_date.date(),
                appointment_time=self.schedule_date.time(),
                pass_code=self.pass_code,
                meeting_url=meeting_url,
            )

        elif self.status == "cancelled":
            message = APPOINTMENT_CANCEL_PATIENT.format(
                user_name=self.patient.name,
                appointment_date=self.schedule_date.date(),
                appointment_time=self.schedule_date.time(),
            )

        if message:
            send_sms(f"{self.patient.phone}", message)

    def system_notification(self):
        push_notification_obj = PushNotification.objects.create(
            title=APPOINTMENT_REMINDER_TITLE,
            message=APPOINTMENT_REMINDER_MESSAGE.format(
                appointment_date=self.schedule_date.date(),
                appointment_time=self.schedule_date.time(),
            ),
            notification_type="system",
        )
        push_notification_obj.save()

        superuser = User.objects.filter(is_superuser=True).first()


        if superuser:
            user_push_notifications = [
                UserPushNotification(user=self.doctor.user, notification=push_notification_obj),
                UserPushNotification(user=superuser, notification=push_notification_obj),
            ]

            UserPushNotification.objects.bulk_create(user_push_notifications)

    def save(self, *args, **kwargs):
        """Send sms to doctor and Patient about change status"""
        if self.status != "pending" and self.status != self.previous_status:
            self.system_notification()
            if settings.IS_PRODUCTION:
                self.send_sms_on_status_change()
        self.previous_status = self.status
        self.meeting_link = f"{os.environ.get('TCS_USER_FRONTEND')}{self.room_name}"
        super(Appointments, self).save(*args, **kwargs)

class Transactions(DateTimeFieldMixin):
    appointment = models.ForeignKey(Appointments, models.DO_NOTHING)
    trans_id = models.CharField(max_length=50)
    paid_amount = models.FloatField()
    pay_mode = models.CharField(max_length=20)

    class Meta:
        db_table = "transactions"

    def __str__(self):
        return f"{self.id}-{self.patient}"

class Consultation(DateTimeFieldMixin):
    appointment = models.ForeignKey(Appointments, on_delete=models.DO_NOTHING)
    prescription = models.TextField()

    class Meta:
        db_table = "consultations"


class NotePad(DateTimeFieldMixin):
    room_name = models.CharField(max_length=50)
    notepad = models.TextField()


class Feedbacks(DateTimeFieldMixin):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "feedbacks"


class DoctorExperience(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    hospital_name = models.CharField(max_length=255)
    position = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "doctor_experience"
        ordering = ["-start_date"]
