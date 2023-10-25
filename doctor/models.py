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
        return self.email


GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
)


class Patients(DateTimeFieldMixin):
    patient_id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    dob = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)

    pre_health_issue = models.BooleanField()
    pre_health_issue_text = models.TextField(null=True, blank=True)

    treatment_undergoing = models.BooleanField()
    treatment_undergoing_text = models.TextField(null=True, blank=True)

    treatment_allergies = models.BooleanField()
    treatment_allergies_text = models.TextField(null=True, blank=True)

    additional_note = models.TextField(null=True, blank=True)

    paid_amount = models.FloatField()
    pay_mode = models.CharField(max_length=20)

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
        return f"{self.name}"


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
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("rescheduled", "Rescheduled"),
    ("free_consultation", "Free Consultation"),
    ("cancelled", "Cancelled"),
    ("unanswered_patient", "Unanswered Patient"),
    ("unanswered_doctor", "Unanswered Doctor"),
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
    slot_key = models.CharField(max_length=5)
    room_name = models.CharField(max_length=50)
    no_cost_consult = models.IntegerField(default=0)
    is_attended = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50, choices=APPOINTMENT_STATUS_CHOICES, default="pending"
    )
    meeting_link = models.URLField()

    class Meta:
        db_table = "appointments"


class Consultation(DateTimeFieldMixin):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    consult = models.TextField()
    prescription = models.ForeignKey(
        Prescriptions, on_delete=models.CASCADE, null=True, blank=True
    )

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
