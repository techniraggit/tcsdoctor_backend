from core.serializers import BaseSerializer, serializers
from doctor.models import *
from accounts.serializers import UserSerializer
from administrator.models import UserPushNotification
from django.utils import timezone


class DoctorAvailabilitySerializer(BaseSerializer):
    class Meta:
        model = DoctorAvailability
        fields = ("id", "start_working_hr", "end_working_hr", "working_days")


class DoctorSerializer(BaseSerializer):
    doctor_availability = DoctorAvailabilitySerializer(many=True, read_only=True)
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
            "priority",
            "summary",
            "appointment_charges",
            "salary",
            "is_active",
            "doctor_availability",
        ]


class UsersSerializer(BaseSerializer):
    class Meta:
        model = Users
        fields = "__all__"


class PatientsSerializer(BaseSerializer):
    user = UsersSerializer()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patients
        fields = "__all__"

    def get_age(self, obj):
        return obj.age()


class AppointmentsSerializer(BaseSerializer):
    patient = PatientsSerializer(read_only=True)
    doctor = DoctorSerializer()

    class Meta:
        model = Appointments
        fields = "__all__"


class AvailabilitySerializer(BaseSerializer):
    class Meta:
        model = Availability
        fields = "__all__"


class ConsultationSerializer(BaseSerializer):
    patient = PatientsSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    appointment = AppointmentsSerializer(read_only=True, fields=["schedule_date"])

    class Meta:
        model = Consultation
        fields = "__all__"
