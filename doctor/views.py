from doctor.serializers import DoctorSerializer
import requests
from django.conf import settings
from django.db import transaction
from doctor.models import (  # Doctor Models
    Users,
    Patients,
    Appointments,
)
from doctor.serializers import (  # Doctor Serializers
    AppointmentsSerializer,
    PatientsSerializer,
    Patients,
    Doctors,
)
from utilities.algo import get_available_time_slots
from rest_framework.response import Response
from rest_framework.views import APIView
from utilities.utils import (
    is_valid_date,
    is_valid_email,
    is_valid_phone,
)
from core.decorators import token_required
from core.mixins import DoctorViewMixin
from rest_framework.decorators import api_view
from administrator.models import UserPushNotification
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from django.shortcuts import render
from django.http import JsonResponse

from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings
from django.db.models import Min, Max
from doctor.models import Doctors

sel = "2023-09-28 12:00"

from django.forms.models import model_to_dict


def get_available_doctor(selected_date):
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d %H:%M")

    date = date_obj.strftime("%Y-%m-%d")
    time = date_obj.strftime("%H:%M:%S")
    day = date_obj.strftime("%A")

    doctors_not_in_appointments = Doctors.objects.filter(
        Q(Q(appointments__status="completed") | Q(appointments__isnull=True))
        & Q(working_days__contains=[day])
        & Q(start_working_hr__lte=time)
        & Q(end_working_hr__gte=time)
    ).exclude(appointments__schedule_date=selected_date)

    high_priority_doctor = doctors_not_in_appointments.filter(priority="high")
    if high_priority_doctor:
        return (high_priority_doctor.order_by("?").values_list("id", flat=True))[0]

    medium_priority_doctor = doctors_not_in_appointments.filter(priority="medium")
    if medium_priority_doctor:
        return (medium_priority_doctor.order_by("?").values_list("id", flat=True))[0]

    low_priority_doctor = doctors_not_in_appointments.filter(priority="low")
    if low_priority_doctor:
        return (low_priority_doctor.order_by("?").values_list("id", flat=True))[0]


@token_required
@api_view(["GET"])
def time_slots(request):
    date = request.GET.get("date")
    if not date:
        return Response(
            {"status": False, "message": "required fields are missing"}, 400
        )
    if not is_valid_date(date, "%Y-%m-%d"):
        return Response(
            {"status": False, "message": "Invalid date format. Please use '%Y-%m-%d'."}
        )

    data = get_available_time_slots(date)
    return Response({"status": True, "data": data})


@token_required
@api_view(["POST"])
def schedule_meeting(request):
    if request.method == "POST":
        data = request.data

        user_required_fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
        ]
        patient_required_fields = [
            "name",
            "phone",
            "email",
            "dob",
            "gender",
            "paid_amount",
            "pay_mode",
            "schedule_date",
        ]
        required = False
        message = ""

        if not all(data["user"].get(field) for field in user_required_fields):
            required = True
            message = "Required fields are missing in 'User'."

        if not all(data["patient"].get(field) for field in patient_required_fields):
            required = True
            message = "Required fields are missing in 'patient'."

        if required:
            return Response({"status": False, "message": message}, 400)

        # Extract user data
        user_id = data["user"].get("id")
        user_first_name = data["user"].get("first_name")
        user_last_name = data["user"].get("last_name")
        user_email = data["user"].get("email")
        user_phone_number = data["user"].get("phone_number")

        # Extract patient data
        patient_name = data["patient"].get("name")
        patient_phone = data["patient"].get("phone")
        patient_email = data["patient"].get("email")
        patient_dob = data["patient"].get("dob")
        patient_gender = data["patient"].get("gender")
        patient_paid_amount = data["patient"].get("paid_amount")
        patient_pay_mode = data["patient"].get("pay_mode")
        patient_schedule_date = data["patient"].get("schedule_date")

        if not is_valid_email(patient_email):
            return Response(
                {
                    "status": False,
                    "message": "Invalid email address format. Please provide a valid email address.",
                },
                400,
            )

        if not is_valid_phone(patient_phone):
            return Response(
                {
                    "status": False,
                    "message": "Invalid phone number. Please provide a valid phone number.",
                },
                400,
            )

        if not is_valid_date(patient_schedule_date, "%Y-%m-%d %H:%M"):
            return Response(
                {
                    "status": False,
                    "message": "Invalid schedule date format. Please use YYYY-MM-DD HH:MM.",
                },
                400,
            )

        if not is_valid_date(patient_dob, "%Y-%m-%d"):
            return Response(
                {
                    "status": False,
                    "message": "Invalid DOB date format. Please use YYYY-MM-DD.",
                },
                400,
            )

        if not isinstance(patient_paid_amount, int or float):
            return Response(
                {
                    "status": False,
                    "message": "Invalid paid amount. Please provide a valid paid amount",
                },
                400,
            )

        try:
            with transaction.atomic():
                users_obj, _ = Users.objects.get_or_create(user_id=user_id)

                users_obj.first_name = user_first_name
                users_obj.last_name = user_last_name
                users_obj.email = user_email
                users_obj.phone_number = user_phone_number
                users_obj.save()

                patient_obj = Patients.objects.create(
                    user=users_obj,
                    name=patient_name,
                    phone=patient_phone,
                    email=patient_email,
                    dob=patient_dob,
                    gender=patient_gender,
                    paid_amount=patient_paid_amount,
                    pay_mode=patient_pay_mode,
                )
                patient_obj.save()

                res_dr = get_available_doctor(patient_schedule_date)

                try:
                    doctor_obj = Doctors.objects.get(pk=res_dr)
                except Exception as e:
                    return Response(
                        {
                            "status": False,
                            "message": "We couldn't find any available doctors. Please make another selection.",
                        },
                        400,
                    )

                appointment_obj = Appointments.objects.create(
                    patient=patient_obj,
                    doctor=doctor_obj,
                    schedule_date=patient_schedule_date,
                    meeting_link="http://0.0.0.0:9000/backend/accounts/user/",
                )

                data = model_to_dict(appointment_obj)

                return Response(
                    {
                        "status": True,
                        "message": "The appointment has been successfully created",
                        "data": data,
                    },
                    201,
                )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong. Please try again later.",
                    "error": str(e),
                },
                400,
            )


@token_required
@api_view(["PATCH"])
def reschedule_meeting(request):
    if request.method == "PATCH":
        date = request.data.get("date")
        time = request.data.get("time")
        appointment_id = request.data.get("appointment_id")

        if not all([date, time, appointment_id]):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )

        datetime_str = date + " " + time
        input_format = "%d-%m-%Y %H:%M"

        schedule_date = datetime.strptime(datetime_str, input_format)

        try:
            appointment_obj = Appointments.objects.get(pk=appointment_id)
        except:
            return Response({"status": False, "message": "Appointment not found"}, 404)

        appointment_obj.doctor
        appointment_obj.schedule_date
        appointment_obj.status
        appointment_obj.meeting_link
        appointment_obj.save()
        return Response(
            {
                "status": True,
                "message": "Appointment has been successfully rescheduled",
            },
            200,
        )


class AppointmentView(DoctorViewMixin):
    def get(self, request):
        search_query = (request.GET.get("search_query", "")).lower()
        list_of_available_search_query = ["pending", "completed", "rescheduled"]

        if search_query:
            if search_query not in list_of_available_search_query:
                return Response(
                    {
                        "status": False,
                        "message": f"Invalid status provided. Please use one of the following: {', '.join(list_of_available_search_query)}",
                    }
                )
            query_set = Appointments.objects.filter(
                doctor__user=request.user, status=search_query
            )

        else:
            query_set = Appointments.objects.filter(doctor__user=request.user)

        data = AppointmentsSerializer(
            query_set,
            many=True,
            fields=["patient", "schedule_date", "status", "filter_by"],
        ).data
        return Response({"status": True, "data": data})


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
        data = AppointmentsSerializer(patients, many=True, fields=["patient"]).data
        return Response({"status": True, "data": data}, 200)


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
        notifications = UserPushNotification.objects.filter(
            user=request.user
        ).select_related("notification")
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
