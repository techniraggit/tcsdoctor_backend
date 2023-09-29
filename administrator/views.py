from core.decorators import admin_required
from rest_framework.decorators import api_view
from administrator.models import PushNotification, UserPushNotification
from administrator.serializers import PushNotificationSerializer
from core.mixins import AdminViewMixin
from utilities.utils import (
    is_valid_date,
    is_valid_email,
    is_valid_phone,
)
from rest_framework.response import Response
from doctor.serializers import (  # Doctor Serializer and Models
    DoctorSerializer,
    Doctors,
    PatientsSerializer,
    Patients,
    Appointments,
    AppointmentsSerializer,
)
from accounts.models import User
from django.db.models import (
    Q,
)
from django.db import transaction
from django.forms.models import model_to_dict
from datetime import datetime


# Create your views here.
def validate_time(start_time, end_time):
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        end_time_obj = datetime.strptime(end_time, "%H:%M")

        if end_time_obj <= start_time_obj:
            return False
        return True
    except ValueError:
        return False

from utilities.pigeon.service import send_sms
from utilities.pigeon.templates import WELCOME
class DoctorView(AdminViewMixin):
    def get(self, request):
        id = request.GET.get("id")
        if id:
            try:
                query_set = Doctors.objects.select_related("user").get(user__id=id)
                data = DoctorSerializer(query_set).data
                return Response({"status": True, "data": data}, 200)
            except:
                data = {}
                return Response({"status": True, "data": data}, 200)
        query_set = Doctors.objects.select_related("user").all().order_by("-created")
        data = DoctorSerializer(query_set, many=True).data
        return Response({"status": True, "data": data}, 200)

    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        profile_image = request.FILES.get("profile_image")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")

        specialization = request.data.get("specialization")
        medical_license = request.FILES.get("medical_license")
        education = request.data.get("education")
        clinic_name = request.data.get("clinic_name")
        clinic_address = request.data.get("clinic_address")
        clinic_contact_no = request.data.get("clinic_contact_no")
        start_working_hr = request.data.get("start_working_hr")
        end_working_hr = request.data.get("end_working_hr")
        working_days = request.data.get("working_days", "").split(",")
        priority = request.data.get("priority")
        summary = request.data.get("summary")
        appointment_charges = request.data.get("appointment_charges")
        salary = request.data.get("salary")

        if not all(
            [
                first_name,
                last_name,
                email,
                phone_number,
                specialization,
                education,
                clinic_name,
                clinic_address,
                start_working_hr,
                end_working_hr,
                working_days,
                priority,
            ]
        ):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )

        if not is_valid_email(email):
            return Response(
                {
                    "status": False,
                    "message": "Invalid email address format. Please provide a valid email address.",
                },
                400,
            )

        if not is_valid_phone(phone_number):
            return Response(
                {
                    "status": False,
                    "message": "Invalid phone number. Please provide a valid phone number.",
                },
                400,
            )

        if not is_valid_date(start_working_hr, "%H:%M") or not is_valid_date(
            end_working_hr, "%H:%M"
        ):
            return Response(
                {
                    "status": False,
                    "message": "Invalid time format. Please use a valid format for the time. (HH:MM)",
                },
                400,
            )

        if not validate_time(start_working_hr, end_working_hr):
            return Response(
                {
                    "status": False,
                    "message": "Invalid combination of start working hours and end working hours",
                },
                400,
            )

        if not isinstance(working_days, list):
            return Response(
                {"status": False, "message": "Working days should be in Array"}, 400
            )

        working_days = [working_day.strip() for working_day in working_days]

        try:
            salary = float(salary)
        except:
            return Response(
                {"status": False, "message": " Invalid value for Salary"}, 400
            )

        try:
            appointment_charges = float(appointment_charges)
        except:
            return Response(
                {"status": False, "message": " Invalid value for Appointment charges"},
                400,
            )

        if clinic_contact_no:
            if not isinstance(clinic_contact_no, str) or len(clinic_contact_no) > 15:
                return Response(
                    {
                        "status": False,
                        "message": "The clinic contact number provided is invalid",
                    },
                    400,
                )

        existing_user = User.objects.filter(
            Q(email=email) | Q(phone_number=phone_number)
        ).first()

        if existing_user:
            if existing_user.email == email:
                message = "Email linked with another account"
            else:
                message = "Phone linked with another account"
            return Response({"status": False, "message": message}, status=400)

        try:
            with transaction.atomic():
                user_obj = User.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    profile_image=profile_image,
                    email=email,
                    phone_number=phone_number,
                    is_staff=True,
                )
                doctor_obj = Doctors.objects.create(
                    user=user_obj,
                    specialization=specialization,
                    medical_license=medical_license,
                    education=education,
                    clinic_name=clinic_name,
                    clinic_address=clinic_address,
                    clinic_contact_no=clinic_contact_no,
                    start_working_hr=start_working_hr,
                    end_working_hr=end_working_hr,
                    working_days=working_days,
                    priority=priority,
                    summary=summary,
                    appointment_charges=appointment_charges,
                    salary=salary,
                )
                send_sms(user_obj.phone_number, WELCOME)
            return Response(
                {
                    "status": True,
                    "message": "Doctor successfully added.",
                    "data": DoctorSerializer(doctor_obj).data,
                },
                201,
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "User addition encountered an issue. Please try again later.",
                    "error": str(e),
                },
                status=500,
            )

    def patch(self, request):
        """update the complete information of Doctor"""
        id = request.data.get("id")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        profile_image = request.FILES.get("profile_image")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")

        specialization = request.data.get("specialization")
        medical_license = request.FILES.get("medical_license")
        education = request.data.get("education")
        clinic_name = request.data.get("clinic_name")
        clinic_address = request.data.get("clinic_address")
        clinic_contact_no = request.data.get("clinic_contact_no")
        start_working_hr = request.data.get("start_working_hr")
        end_working_hr = request.data.get("end_working_hr")
        working_days = request.data.get("working_days", "").split(",")
        priority = request.data.get("priority")
        summary = request.data.get("summary")
        appointment_charges = request.data.get("appointment_charges")
        salary = request.data.get("salary")

        if not all(
            [
                id,
                first_name,
                last_name,
                email,
                phone_number,
                specialization,
                education,
                clinic_name,
                clinic_address,
                start_working_hr,
                end_working_hr,
                working_days,
                priority,
            ]
        ):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )

        if not is_valid_email(email):
            return Response(
                {
                    "status": False,
                    "message": "Invalid email address format. Please provide a valid email address.",
                },
                400,
            )

        if not is_valid_phone(phone_number):
            return Response(
                {
                    "status": False,
                    "message": "Invalid phone number. Please provide a valid phone number.",
                },
                400,
            )

        if not is_valid_date(start_working_hr, "%H:%M") or not is_valid_date(
            end_working_hr, "%H:%M"
        ):
            return Response(
                {
                    "status": False,
                    "message": "Invalid time format. Please use a valid format for the time. (HH:MM)",
                },
                400,
            )

        if not isinstance(working_days, list):
            return Response(
                {"status": False, "message": "Days off should be in Array"}, 400
            )

        working_days = [working_day.strip() for working_day in working_days]

        try:
            salary = float(salary)
        except:
            return Response(
                {"status": False, "message": " Invalid value for Salary"}, 400
            )

        try:
            appointment_charges = float(appointment_charges)
        except:
            return Response(
                {"status": False, "message": " Invalid value for Appointment charges"},
                400,
            )

        existing_user = (
            User.objects.exclude(id=id)
            .filter(Q(email=email) | Q(phone_number=phone_number))
            .first()
        )

        if existing_user:
            if existing_user.email == email:
                message = "Email linked with another account"
            else:
                message = "Phone linked with another account"
            return Response({"status": False, "message": message}, status=400)

        try:
            user_obj = User.objects.get(id=id)
            doctor_obj = Doctors.objects.select_related("user").get(user__id=id)

        except Doctors.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Doctor not found",
                    "detail": "Doctor does not exist in records",
                },
                404,
            )

        except Doctors.MultipleObjectsReturned:
            return Response(
                {
                    "status": False,
                    "message": "Doctor not found",
                    "detail": "Multiple doctor records found",
                },
                404,
            )

        except:
            return Response(
                {
                    "status": False,
                    "message": "Doctor not found",
                    "detail": "An error occurred while searching for a doctor.",
                },
                404,
            )

        try:
            with transaction.atomic():
                user_obj.first_name = first_name
                user_obj.last_name = last_name
                if profile_image:
                    user_obj.profile_image = profile_image
                user_obj.email = email
                user_obj.phone_number = phone_number
                user_obj.save()

                doctor_obj.specialization = specialization
                if medical_license:
                    doctor_obj.medical_license = medical_license
                doctor_obj.education = education
                doctor_obj.clinic_name = clinic_name
                doctor_obj.clinic_address = clinic_address
                doctor_obj.clinic_contact_no = clinic_contact_no
                doctor_obj.start_working_hr = start_working_hr
                doctor_obj.end_working_hr = end_working_hr
                doctor_obj.working_days = working_days
                doctor_obj.priority = priority
                doctor_obj.summary = summary
                doctor_obj.appointment_charges = appointment_charges
                doctor_obj.salary = salary
                doctor_obj.save()
            return Response(
                {
                    "status": True,
                    "message": "Doctor updated successfully",
                    "data": DoctorSerializer(doctor_obj).data,
                },
                200,
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong. Please try again later",
                    "error": str(e),
                },
                500,
            )

    def put(self, request):
        """To switch the active status of Doctor"""
        id = request.GET.get("id")
        if not id:
            return Response({"status": False, "message": "ID is required"}, 400)

        try:
            doctor_obj = Doctors.objects.get(user__id=id)
        except:
            return Response({"status": False, "message": "Doctor not found"}, 404)

        doctor_obj.is_active = not doctor_obj.is_active
        doctor_obj.save()
        return Response(
            {
                "status": True,
                "message": "Status updated successfully",
                "data": DoctorSerializer(doctor_obj).data,
            },
            200,
        )


class PatientView(AdminViewMixin):
    def get(self, request):
        query_set = Patients.objects.all().select_related("user")
        data = PatientsSerializer(query_set, many=True).data
        return Response({"status": True, "data": data})


LIST_OF_AVAILABLE_QUERY = ["pending", "completed", "rescheduled"]


class AppointmentView(AdminViewMixin):
    def get(self, request):
        doctor_id = request.GET.get("id")
        search_query = (request.GET.get("search_query", "")).lower()
        appointment_id = request.GET.get("appointment_id")

        if appointment_id:
            try:
                query_set = Appointments.objects.get(pk=appointment_id)
            except:
                return Response(
                    {"status": False, "message": "Appointment not found"}, 404
                )

            data = AppointmentsSerializer(query_set).data
            return Response({"status": True, "data": data})

        if not doctor_id:
            return Response({"status": False, "message": "ID is required"}, 400)

        if search_query:
            if search_query not in LIST_OF_AVAILABLE_QUERY:
                return Response(
                    {
                        "status": False,
                        "message": f"Invalid query provided. Please use one of the following: {', '.join(LIST_OF_AVAILABLE_QUERY)}",
                    }
                )
            query_set = Appointments.objects.filter(
                doctor__user__id=doctor_id, status=search_query
            )
        else:
            query_set = Appointments.objects.filter(doctor__id=doctor_id)

        data = AppointmentsSerializer(query_set, many=True).data
        return Response({"status": True, "data": data})


@admin_required
@api_view(["GET"])
def get_push_notification_types(request):
    notification_types = PushNotification.NOTIFICATION_TYPE_CHOICE
    notification_types = [i[0] for i in notification_types]
    return Response({"status": True, "notification_types": notification_types}, 200)


@admin_required
@api_view(["GET"])
def get_all_doctors_email(request):
    doctor_emails = (
        Doctors.objects.all()
        .select_related("user")
        .values_list("user__email", flat=True)
    )
    return Response({"status": True, "doctor_emails": doctor_emails}, 200)


class PushNotificationView(AdminViewMixin):
    def get(self, request):
        push_notifications = PushNotificationSerializer(
            PushNotification.objects.all().order_by("-id"),
            fields=["-updated"],
            many=True,
        )

        return Response(
            {"status": True, "push_notifications": push_notifications.data}, 200
        )

    def post(self, request):
        user_emails = request.data.get("user_emails")
        title = request.data.get("title")
        message = request.data.get("message")
        notification_type = request.data.get("notification_type")

        if not all([user_emails, title, message, notification_type]):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )

        users_list = User.objects.filter(email__in=user_emails)

        push_notification_obj = PushNotification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
        )
        push_notification_obj.save()

        users_notification_list = [
            UserPushNotification(user=user, notification=push_notification_obj)
            for user in users_list
        ]

        UserPushNotification.objects.bulk_create(users_notification_list)

        return Response({"status": True, "message": "Notification sent"}, 201)


DOWNLOAD_ACTIONS_LIST = [
    "appointment_report",
    "financial_report",
    "salary_and_payment_report",
]
from openpyxl.writer.excel import save_virtual_workbook
from django.http import HttpResponse
from openpyxl import Workbook


class DownloadReportView(AdminViewMixin):
    def get(self, request):
        action = request.GET.get("action", "").lower()
        if not action:
            return Response(
                {"status": False, "message": "Action value is required"}, 400
            )

        if action not in DOWNLOAD_ACTIONS_LIST:
            return Response(
                {
                    "status": False,
                    "message": f"Invalid action provided. Please use one of the following: {', '.join(DOWNLOAD_ACTIONS_LIST)}.",
                }
            )

        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # APPOINTMENT REPORT
        if action == "appointment_report":
            doctor_id = request.GET.get("doctor_id")
            if not doctor_id:
                return Response({"status": False, "message": "Doctor id required"}, 400)
            appointments = Appointments.objects.filter(
                doctor__user__id=doctor_id
            ).select_related("patient")
            appointments_headers = [
                "Name",
                "Phone#",
                "DOB",
                "Gender",
                "Paid Amount",
                "Pay Mode",
                "Scheduled Date",
                "Current Status",
                "Meeting Link",
            ]

            worksheet.append(appointments_headers)
            for appointment in appointments:
                row = [
                    appointment.patient.name,
                    appointment.patient.phone,
                    appointment.patient.dob.strftime("%b %d, %Y"),
                    appointment.patient.gender.capitalize(),
                    appointment.patient.paid_amount,
                    appointment.patient.pay_mode,
                    appointment.schedule_date.strftime("%b %d, %Y %I:%M %p"),
                    appointment.status,
                    appointment.meeting_link,
                ]
                worksheet.append(row)
            worksheet.column_dimensions["A"].width = 20  # NAME
            worksheet.column_dimensions["B"].width = 15  # PHONE
            worksheet.column_dimensions["C"].width = 15  # DOB
            worksheet.column_dimensions["D"].width = 15  # GENDER
            worksheet.column_dimensions["E"].width = 10  # PAID AMOUNT
            worksheet.column_dimensions["F"].width = 10  # PAY MODE
            worksheet.column_dimensions["G"].width = 22  # SCHEDULE DATE
            worksheet.column_dimensions["H"].width = 18  # STATUS
            worksheet.column_dimensions["I"].width = 20  # MEETING LINK
            virtual_excel_file = save_virtual_workbook(workbook)
            response[
                "Content-Disposition"
            ] = f"attachment; filename={doctor_id}_appointment_report.xlsx"
            response.write(virtual_excel_file)

        # FINANCIAL REPORT
        elif action == "financial_report":
            pass

        return response
