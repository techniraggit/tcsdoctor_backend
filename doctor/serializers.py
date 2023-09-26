from core.serializers import BaseSerializer, serializers
from doctor.models import *
from accounts.serializers import UserSerializer
from administrator.models import UserPushNotification
from django.utils import timezone


class DoctorSerializer(BaseSerializer):
    user = UserSerializer(
        fields=[
            "id",
            "first_name",
            "last_name",
            "profile_image",
            "email",
            "phone_number",
            "is_active",
            "created",
        ]
    )

    class Meta:
        model = Doctors
        fields = [
            "user",
            "specialization",
            "medical_license",
            "education",
            "clinic_name",
            "clinic_address",
            "clinic_contact_no",
            "start_working_hr",
            "end_working_hr",
            "working_days",
            "priority",
            "summary",
            "appointment_charges",
            "salary",
            "is_active",
        ]


class UsersSerializer(BaseSerializer):
    class Meta:
        model = Users
        fields = "__all__"


class PatientsSerializer(BaseSerializer):
    user = UsersSerializer()

    class Meta:
        model = Patients
        fields = "__all__"


class AppointmentsSerializer(BaseSerializer):
    patient = PatientsSerializer(read_only=True, fields=["-user"])
    doctor = DoctorSerializer()
    # filter_by = serializers.SerializerMethodField()

    class Meta:
        model = Appointments
        fields = "__all__"

    # # schedule_date, status
    # def get_filter_by(self, obj):
    #     if obj.status == "completed":
    #         return "Completed"
    #     elif obj.status == "pending": #and obj.schedule_date > timezone.now:
    #         return "Upcoming"
    #     else:
    #         return obj.status == "rescheduled"
