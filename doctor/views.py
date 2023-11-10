from utilities.utils import time_localize
from utilities.utils import generate_otp
from utilities.pigeon.service import send_email
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from doctor.models import (  # Doctor Models
    Patients,
    Appointments,
    Consultation,
    Doctors,
)
from doctor.serializers import (  # Doctor Serializers
    AppointmentsSerializer,
    PatientsSerializer,
    Patients,
    Doctors,
    AvailabilitySerializer,
    ConsultationSerializer,
    DoctorSerializer,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from utilities.utils import (  # Utils
    is_valid_date,
    is_valid_email,
    is_valid_phone,
    get_room_no,
)
from core.decorators import token_required
from core.mixins import DoctorViewMixin
from rest_framework.decorators import api_view
from administrator.models import UserPushNotification, UserPaymentPrice  # Admin models
from administrator.serializers import UserPaymentPriceSerializer  # Admin Serializers
from datetime import (  # Datetime
    datetime,
    timedelta,
)
from django.db.models import (
    F,
    Q,
)


class AppointmentView(DoctorViewMixin):
    def get(self, request):
        search_query = (request.GET.get("search_query", "")).lower()
        list_of_available_search_query = ["scheduled", "completed", "rescheduled"]
        filter_by_date = request.GET.get("date")
        Appointments_obj = Appointments.objects.filter(
            doctor__user=request.user
        ).order_by("-created")

        if search_query:
            if search_query not in list_of_available_search_query:
                return Response(
                    {
                        "status": False,
                        "message": f"Invalid status provided. Please use one of the following: {', '.join(list_of_available_search_query)}",
                    }
                )
            if search_query == "scheduled":
                query_set = Appointments_obj.filter(
                    status=search_query, schedule_date__date__gte=datetime.now().date()
                )
            elif search_query == "completed":
                query_set = Appointments_obj.filter(status=search_query)
            elif search_query == "rescheduled":
                query_set = Appointments_obj.filter(
                    status=search_query, schedule_date__date__gte=datetime.now().date()
                )

        elif filter_by_date:
            if not is_valid_date(filter_by_date, "%Y-%m-%d"):
                return Response(
                    {
                        "status": False,
                        "message": "Invalid schedule date format. Please use YYYY-MM-DD",
                    },
                    400,
                )
            query_set = Appointments_obj.filter(schedule_date__date=filter_by_date)

        else:
            query_set = Appointments_obj

        data = AppointmentsSerializer(
            query_set,
            many=True,
            fields=[
                "appointment_id",
                "room_name",
                "patient",
                "schedule_date",
                "status",
                "filter_by",
            ],
        ).data

        display_data = {
            "number_of_appointments": Appointments_obj.count(),
            "unanswered_patient": Appointments_obj.filter(
                is_attend_by_user=False, is_attend_by_doctor=True
            ).count(),
        }
        return Response(
            {"status": True, "data": data, "display_data": display_data}, 200
        )


class PatientView(DoctorViewMixin):
    def get(self, request):
        patient_id = request.GET.get("patient_id")
        if patient_id:
            patients = Appointments.objects.filter(
                doctor__user=request.user, patient__patient_id=patient_id
            ).select_related("patient")
        else:
            patients = Appointments.objects.filter(
                doctor__user=request.user
            ).select_related("patient")
        data = AppointmentsSerializer(
            patients.order_by("-created"), many=True, fields=["patient"]
        ).data
        return Response({"status": True, "data": data}, 200)


class PatientDetailView(DoctorViewMixin):
    def get(self, request):
        user_id = request.GET.get("user_id")
        patient_id = request.GET.get("patient_id")

        if not all([user_id, patient_id]):
            return Response(
                {"status": False, "message": "required fields are missing"}, 400
            )

        patient_obj = Patients.objects.filter(
            patient_id=patient_id, user__user_id=user_id
        ).first()
        if not patient_obj:
            return Response({"status": False, "message": "Patient not found"}, 404)
        appointments = Appointments.objects.filter(
            patient=patient_obj, doctor__user=request.user
        ).order_by("-created")

        consultation_obj = Consultation.objects.filter(appointment__in=appointments)

        consultation_data = ConsultationSerializer(
            consultation_obj, many=True, fields=["appointment", "prescription"]
        ).data
        patient_data = PatientsSerializer(patient_obj, fields=["-user"]).data
        appointments_data = {
            "no_of_appointment": appointments.count(),
            "date_time": appointments.first().schedule_date if appointments else "00",
        }
        return Response(
            {
                "status": True,
                "consultation_data": consultation_data,
                "patient_data": patient_data,
                "appointments_data": appointments_data,
            },
            200,
        )


class ProfileView(DoctorViewMixin):
    def get(self, request):
        try:
            doctor_obj = Doctors.objects.get(user=request.user)
        except:
            return Response({"status": False, "message": "Doctor not found"})

        data = DoctorSerializer(doctor_obj).data
        return Response({"status": True, "data": data})


class NotificationsView(DoctorViewMixin):
    def get(self, request):
        notifications = (
            UserPushNotification.objects.filter(user=request.user)
            .select_related("notification")
            .order_by("-created")
        )
        push_notification = []
        for notification in notifications:
            push_notification.append(
                {
                    "id": notification.id,
                    "title": notification.notification.title,
                    "message": notification.notification.message,
                    "created": notification.notification.created,
                    "is_read": notification.is_read,
                }
            )
        return Response({"status": True, "notifications": push_notification}, 200)

    def put(self, request):
        id = request.data.get("id")
        if not id:
            return Response({"status": False, "message": "id not found"}, 400)

        try:
            dr_notification = UserPushNotification.objects.get(id=id)
        except:
            return Response({"status": False, "message": "Notification not found"}, 404)
        dr_notification.is_read = True
        dr_notification.save()
        data = [
            {
                "id": dr_notification.id,
                "title": dr_notification.notification.title,
                "message": dr_notification.notification.message,
                "created": dr_notification.notification.created,
                "is_read": dr_notification.is_read,
            }
        ]
        return Response({"status": True, "notifications": data})


class ConsultView(DoctorViewMixin):
    def post(self, request):
        notepad = request.data.get("notepad")
        room_name = request.data.get("room_name")
        if not all([notepad, room_name]):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )
        try:
            appointment_obj = Appointments.objects.get(room_name=room_name)
        except:
            return Response({"status": False, "message": "Room not found"}, 404)

        try:
            consultation_obj = Consultation.objects.create(
                prescription=notepad,
                appointment=appointment_obj,
            )

            # ----------------------------Prescription Email to Patient Start--------------------------
            doctor_full_name = f"{appointment_obj.doctor.user.first_name} {appointment_obj.doctor.user.last_name}"
            subject = f"Your Prescription from {doctor_full_name}"
            patient_email = appointment_obj.patient.email
            context = {
                "doctor_name": doctor_full_name,
                "patient_name": f"{appointment_obj.patient.name}",
                "prescription_date": f"{time_localize(consultation_obj.created)}",
                "patient_dob": f"{appointment_obj.patient.dob}",
                "clinic_name": f"{appointment_obj.doctor.clinic_name}",
                "clinic_contact_number": f"{appointment_obj.doctor.clinic_contact_no}",
                "prescription_details": f"{consultation_obj.prescription}",
            }
            body = render_to_string("email/prescription.html", context=context)
            send_email(subject, body, [patient_email])
            # ----------------------------Prescription Email to Patient End--------------------------
            return Response(
                {"status": True, "message": "Your submission was successful"}
            )
        except Exception as e:
            return Response({"status": False, "message": str(e)}, 400)


class ValidateCallDoctorView(DoctorViewMixin):
    def get(self, request):
        room_name = request.GET.get("room_name")
        if not room_name:
            return Response({"status": False, "message": "room name required"}, 400)
        try:
            Appointments_obj = Appointments.objects.get(room_name=room_name)
            Appointments_obj.is_attend_by_doctor = True
            Appointments_obj.save()
            return Response({"status": True, "message": "updated successfully"}, 200)
        except:
            return Response({"status": False, "message": "Meeting not found"}, 404)
