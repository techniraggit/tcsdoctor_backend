from scripts.update_slots import UpdateSlot, DeleteSlot
from datetime import (  # Datetime
    timedelta,
    datetime,
)
import json
from django.db.models import (  # django.db.models
    Sum,
    Case,
    When,
    IntegerField,
    Count,
    Q,
    Max,
    Min,
)
from utilities.pigeon.service import send_sms
from openpyxl import Workbook
from django.http import HttpResponse
from openpyxl.writer.excel import save_virtual_workbook
from utilities.pigeon.templates import WELCOME
from core.decorators import admin_required
from rest_framework.decorators import api_view
from administrator.models import (  # Admin Models
    PushNotification,
    UserPushNotification,
    UserPaymentPrice,
)
from administrator.serializers import (  # Admin Serializer
    PushNotificationSerializer,
    UserPaymentPriceSerializer,
)
from core.mixins import AdminViewMixin
from utilities.utils import (  # Utilities.utils
    is_valid_date,
    is_valid_email,
    is_valid_phone,
)
from rest_framework.response import Response
from doctor.serializers import (  # Doctor Serializers
    DoctorSerializer,
    PatientsSerializer,
    AppointmentsSerializer,
)
from doctor.models import (  # Doctor Models
    Doctors,
    Patients,
    Appointments,
    Availability,
    Transactions,
    DoctorAvailability,
)
from accounts.models import User
from django.db import transaction
from django.utils import timezone
from django.db.models.functions import TruncDate


# Create your views here.
def get_percentage(today_total, yesterday_total):
    try:
        value = round(((today_total - yesterday_total) / yesterday_total), 2)
    except:
        value = 0.0
    return value


def get_start_end_dates_current_week():
    today = datetime.today()
    current_weekday = today.weekday()
    start_date = today - timedelta(days=current_weekday)
    end_date = start_date + timedelta(days=6)

    return start_date.date(), end_date.date()


class DashboardView(AdminViewMixin):
    def get(self, request):
        Doctors_obj = Doctors.objects.all()
        Patients_obj = Patients.objects.all()
        Appointments_obj = Appointments.objects.all()

        # ------------------Utils---------------------------------
        today_date = timezone.now()
        yesterday_date = today_date - timezone.timedelta(days=1)

        # ------------------Doctor---------------------------------
        total_doctors = Doctors_obj.count()
        today_new_doctors_added = Doctors_obj.filter(
            created__date=today_date.date()
        ).count()
        yesterday_total_doctors = Doctors_obj.filter(
            created__date=yesterday_date.date()
        ).count()
        incremented_doctor_percent = get_percentage(
            today_new_doctors_added, yesterday_total_doctors
        )

        # ------------------Patient---------------------------------
        total_patients = Patients_obj.count()
        today_new_patient_added = Patients_obj.filter(
            created__date=today_date.date()
        ).count()
        yesterday_total_patient = Patients_obj.filter(
            created__date=yesterday_date.date()
        ).count()
        incremented_patient_percent = get_percentage(
            today_new_patient_added, yesterday_total_patient
        )

        # ------------------Appointment---------------------------------
        total_appointments = Appointments_obj.count()
        today_new_appointment_added = Appointments_obj.filter(
            created__date=today_date.date()
        ).count()
        yesterday_total_appointment = Appointments_obj.filter(
            created__date=yesterday_date.date()
        ).count()
        incremented_appointment_percent = get_percentage(
            today_new_appointment_added, yesterday_total_appointment
        )

        # ------------------Total Revenue Start---------------------------------
        start_date, end_date = get_start_end_dates_current_week()
        dates_in_current_week = [start_date + timedelta(days=i) for i in range(7)]

        transactions_obj = (
            Transactions.objects.filter(created__range=[start_date, end_date])
            .values("created__date")
            .annotate(total_paid=Sum("paid_amount"))
            .order_by("created__date")
        )

        revenue = []
        for date_entry in dates_in_current_week:
            data = transactions_obj.filter(created__date=date_entry)
            revenue.append(
                {
                    "day": date_entry.strftime("%A"),
                    "total_paid": data.first().get("total_paid") if data else 0,
                }
            )
        # ------------------Total Revenue End---------------------------------

        # ------------------Patient Appointment Start---------------------------------

        # Get the current date and the last month date
        current_date = timezone.now()
        last_month_date = current_date - timedelta(days=current_date.day)

        # Calculate the number of days in the current and last month
        days_in_current_month = (
            current_date.replace(day=28) + timedelta(days=4)
        ).replace(day=1) - timedelta(days=1)
        days_in_last_month = (
            last_month_date.replace(day=28) + timedelta(days=4)
        ).replace(day=1) - timedelta(days=1)

        # Generate a list of past and future days in the current month
        past_days = [current_date - timedelta(days=i) for i in range(current_date.day)]
        future_days = [
            current_date + timedelta(days=i + 1)
            for i in range(days_in_current_month.day - current_date.day)
        ]
        past_days.reverse()
        all_days_current_month = past_days + future_days

        # Generate a list of days in the last month
        all_days_last_month = [
            last_month_date - timedelta(days=i) for i in range(days_in_last_month.day)
        ]
        all_days_last_month.reverse()

        # Day-wise counts for the current month
        current_month_appointment_counts = (
            Appointments.objects.filter(
                schedule_date__month=current_date.month,
                schedule_date__year=current_date.year,
            )
            .annotate(day=TruncDate("schedule_date"))
            .values("day")
            .annotate(count=Count("appointment_id"))
            .order_by("day")
        )

        # Day-wise counts for the last month
        last_month_appointment_counts = (
            Appointments.objects.filter(
                schedule_date__month=last_month_date.month,
                schedule_date__year=last_month_date.year,
            )
            .annotate(day=TruncDate("schedule_date"))
            .values("day")
            .annotate(count=Count("appointment_id"))
            .order_by("day")
        )

        # Create dictionaries to hold the appointment counts
        current_month_counts_dict = {
            entry["day"]: entry["count"] for entry in current_month_appointment_counts
        }
        last_month_counts_dict = {
            entry["day"]: entry["count"] for entry in last_month_appointment_counts
        }

        # Populate day-wise appointment counts for the current month
        current_month_appointment_counts_with_zeros = [
            {"day": day, "count": current_month_counts_dict.get(day.date(), 0)}
            for day in all_days_current_month
        ]

        # Populate day-wise appointment counts for the last month
        last_month_appointment_counts_with_zeros = [
            {"day": day, "count": last_month_counts_dict.get(day.date(), 0)}
            for day in all_days_last_month
        ]

        # ------------------Patient Appointment End---------------------------------

        doctor = {
            "total_doctors": total_doctors,
            "today_new_doctors_added": today_new_doctors_added,
            "incremented_doctor_percent": incremented_doctor_percent,
        }

        patient = {
            "total_patients": total_patients,
            "incremented_patient_percent": incremented_patient_percent,
        }

        appointment = {
            "total_appointments": total_appointments,
            "incremented_appointment_percent": incremented_appointment_percent,
        }

        appointment_graph = {
            "current_month_gp": current_month_appointment_counts_with_zeros,
            "last_month_gp": last_month_appointment_counts_with_zeros,
        }

        analytics_data = {
            "doctor": doctor,
            "patient": patient,
            "appointment": appointment,
            "revenue_graph": revenue,
            "appointment_graph": appointment_graph,
        }
        return Response({"status": True, "data": analytics_data}, 200)


def validate_time(start_time, end_time):
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        end_time_obj = datetime.strptime(end_time, "%H:%M")

        if end_time_obj <= start_time_obj:
            return False
        return True
    except ValueError:
        return False


class DoctorView(AdminViewMixin):
    def get(self, request):
        id = request.GET.get("id")
        search_query = request.GET.get("search_query")
        if search_query:
            query_set = (
                Doctors.objects.select_related("user")
                .filter(
                    Q(user__first_name__icontains=search_query)
                    | Q(user__last_name__icontains=search_query)
                    | Q(user__email__icontains=search_query)
                    | Q(user__phone_number__icontains=search_query)
                )
                .order_by("-created")
            )
            data = DoctorSerializer(query_set, many=True).data
            return Response({"status": True, "data": data}, 200)

        if id:
            try:
                query_set = Doctors.objects.select_related("user").get(user__id=id)
                doctor_profile = DoctorSerializer(query_set).data

                # ------------------Patient Appointment Graph Start---------------------------------

                # Get the current date and the last month date
                current_date = timezone.now()
                last_month_date = current_date - timedelta(days=current_date.day)

                # Calculate the number of days in the current and last month
                days_in_current_month = (
                    current_date.replace(day=28) + timedelta(days=4)
                ).replace(day=1) - timedelta(days=1)
                days_in_last_month = (
                    last_month_date.replace(day=28) + timedelta(days=4)
                ).replace(day=1) - timedelta(days=1)

                # Generate a list of past and future days in the current month
                past_days = [
                    current_date - timedelta(days=i) for i in range(current_date.day)
                ]
                future_days = [
                    current_date + timedelta(days=i + 1)
                    for i in range(days_in_current_month.day - current_date.day)
                ]
                past_days.reverse()
                all_days_current_month = past_days + future_days

                # Generate a list of days in the last month
                all_days_last_month = [
                    last_month_date - timedelta(days=i)
                    for i in range(days_in_last_month.day)
                ]
                all_days_last_month.reverse()

                # Day-wise counts for the current month
                current_month_appointment_counts = (
                    Appointments.objects.filter(
                        doctor=query_set,
                        schedule_date__month=current_date.month,
                        schedule_date__year=current_date.year,
                    )
                    .annotate(day=TruncDate("schedule_date"))
                    .values("day")
                    .annotate(count=Count("appointment_id"))
                    .order_by("day")
                )

                # Day-wise counts for the last month
                last_month_appointment_counts = (
                    Appointments.objects.filter(
                        doctor=query_set,
                        schedule_date__month=last_month_date.month,
                        schedule_date__year=last_month_date.year,
                    )
                    .annotate(day=TruncDate("schedule_date"))
                    .values("day")
                    .annotate(count=Count("appointment_id"))
                    .order_by("day")
                )

                # Create dictionaries to hold the appointment counts
                current_month_counts_dict = {
                    entry["day"]: entry["count"]
                    for entry in current_month_appointment_counts
                }
                last_month_counts_dict = {
                    entry["day"]: entry["count"]
                    for entry in last_month_appointment_counts
                }

                # Populate day-wise appointment counts for the current month
                current_month_appointment_counts_with_zeros = [
                    {"day": day, "count": current_month_counts_dict.get(day.date(), 0)}
                    for day in all_days_current_month
                ]

                # Populate day-wise appointment counts for the last month
                last_month_appointment_counts_with_zeros = [
                    {"day": day, "count": last_month_counts_dict.get(day.date(), 0)}
                    for day in all_days_last_month
                ]

                # ------------------Patient Appointment End---------------------------------

                # ------------------Total Revenue Start---------------------------------
                start_date, end_date = get_start_end_dates_current_week()
                dates_in_current_week = [
                    start_date + timedelta(days=i) for i in range(7)
                ]

                transactions_obj = (
                    Transactions.objects.filter(
                        created__range=[start_date, end_date],
                        appointment__doctor=query_set,
                    )
                    .values("created__date")
                    .annotate(total_paid=Sum("paid_amount"))
                    .order_by("created__date")
                )

                revenue = []
                for date_entry in dates_in_current_week:
                    data = transactions_obj.filter(created__date=date_entry)
                    revenue.append(
                        {
                            "day": date_entry.strftime("%A"),
                            "total_paid": data.first().get("total_paid") if data else 0,
                        }
                    )
                # ------------------Total Revenue End---------------------------------

                patient_appointment_graph = {
                    "current_month": current_month_appointment_counts_with_zeros,
                    "last_month": last_month_appointment_counts_with_zeros,
                }
                graphs = {
                    "revenue": revenue,
                    "patient_appointment_graph": patient_appointment_graph,
                }
                return Response(
                    {"status": True, "data": doctor_profile, "graphs": graphs}, 200
                )
            except Exception as e:
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
        priority = request.data.get("priority")
        summary = request.data.get("summary")
        appointment_charges = request.data.get("appointment_charges")
        salary = request.data.get("salary")
        availability = request.data.get("availability")

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
                availability,
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

        try:
            availability = json.loads(availability)
        except:
            # if not isinstance(availability, list):
            return Response(
                {
                    "status": False,
                    "message": "The format for the availability is not valid",
                },
                400,
            )

        for avail in availability:
            if not is_valid_date(
                avail.get("start_working_hr"), "%H:%M"
            ) or not is_valid_date(avail.get("end_working_hr"), "%H:%M"):
                return Response(
                    {
                        "status": False,
                        "message": "Invalid time format. Please use a valid format for the time. (HH:MM)",
                    },
                    400,
                )

            if not validate_time(
                avail.get("start_working_hr"), avail.get("end_working_hr")
            ):
                return Response(
                    {
                        "status": False,
                        "message": "Invalid combination of start working hours and end working hours",
                    },
                    400,
                )

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
                    priority=priority,
                    summary=summary,
                    appointment_charges=appointment_charges,
                    salary=salary,
                )

                doctor_availability_list = []
                for avail in availability:
                    working_days = (avail["working_days"]).split(",")
                    working_days = [working_day.strip() for working_day in working_days]
                    doctor_availability_list.append(
                        DoctorAvailability(
                            doctor=doctor_obj,
                            start_working_hr=avail["start_working_hr"],
                            end_working_hr=avail["end_working_hr"],
                            working_days=working_days,
                        )
                    )
                DoctorAvailability.objects.bulk_create(doctor_availability_list)

                # sms_status = send_sms(user_obj.phone_number, WELCOME)
                # if not sms_status:
                #     return Response(
                #         {
                #             "status": False,
                #             "message": "Message sending failed. Please try again later.",
                #         },
                #         500,
                #     )
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
        priority = request.data.get("priority")
        summary = request.data.get("summary")
        appointment_charges = request.data.get("appointment_charges")
        salary = request.data.get("salary")
        availability = request.data.get("availability")

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
                availability,
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

        try:
            availability = json.loads(availability)
        except:
            # if not isinstance(availability, list):
            return Response(
                {
                    "status": False,
                    "message": "The format for the availability is not valid",
                },
                400,
            )

        for avail in availability:
            if not is_valid_date(
                avail.get("start_working_hr"), "%H:%M"
            ) or not is_valid_date(avail.get("end_working_hr"), "%H:%M"):
                return Response(
                    {
                        "status": False,
                        "message": "Invalid time format. Please use a valid format for the time. (HH:MM)",
                    },
                    400,
                )

            if not validate_time(
                avail.get("start_working_hr"), avail.get("end_working_hr")
            ):
                return Response(
                    {
                        "status": False,
                        "message": "Invalid combination of start working hours and end working hours",
                    },
                    400,
                )

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

                doctor_obj.priority = priority
                doctor_obj.summary = summary
                doctor_obj.appointment_charges = appointment_charges
                doctor_obj.salary = salary
                doctor_obj.save()

                for avail in availability:
                    working_days = (avail["working_days"]).split(",")
                    working_days = [working_day.strip() for working_day in working_days]
                    start_working_hr = avail["start_working_hr"]
                    end_working_hr = avail["end_working_hr"]
                    id = avail.get("id")
                    try:
                        if id:
                            doctor_availability = DoctorAvailability.objects.get(pk=id)
                            doctor_availability.working_days = working_days
                            doctor_availability.start_working_hr = start_working_hr
                            doctor_availability.end_working_hr = end_working_hr
                            doctor_availability.save()
                        else:
                            DoctorAvailability.objects.create(
                                doctor=doctor_obj,
                                working_days=working_days,
                                start_working_hr=start_working_hr,
                                end_working_hr=end_working_hr,
                            )
                    except:
                        continue
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

        active_status = not doctor_obj.is_active
        doctor_obj.is_active = active_status
        doctor_obj.user.is_active = active_status
        doctor_obj.user.save()
        doctor_obj.save()
        return Response(
            {
                "status": True,
                "message": "Status updated successfully",
                "data": DoctorSerializer(doctor_obj).data,
            },
            200,
        )


class RemoveAvailTimeView(AdminViewMixin):
    def patch(self, request):
        id = request.data.get("id")
        if not id:
            return Response({"status": False, "message": "Id required"}, 400)
        try:
            doctor_availability = DoctorAvailability.objects.get(pk=id)
            doctor_availability.delete()
            return Response(
                {"status": True, "message": "Doctor Availability removed successfully"},
                200,
            )
        except:
            return Response(
                {"status": False, "message": "Doctor Availability not found"}, 404
            )


class PatientView(AdminViewMixin):
    def get(self, request):
        query_set = Patients.objects.all().select_related("user").order_by("-created")
        data = PatientsSerializer(query_set, many=True).data
        return Response({"status": True, "data": data})


LIST_OF_AVAILABLE_QUERY = ["scheduled", "completed", "rescheduled"]

from doctor.serializers import ConsultationSerializer, Consultation
from django.utils import timezone
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
            consultation_query = Consultation.objects.filter(appointment=query_set)
            consultation_data = ConsultationSerializer(consultation_query, many=True, fields=["prescription"]).data
            return Response({"status": True, "data": data, "consultation_data": consultation_data})

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
            if search_query == "completed":
                query_set = Appointments.objects.filter(
                    doctor__user__id=doctor_id, status=search_query
                ).order_by("-created")
            else:
                query_set = Appointments.objects.filter(
                    doctor__user__id=doctor_id, status=search_query, schedule_date__gte=timezone.now()
                ).order_by("-created")
        else:
            query_set = Appointments.objects.filter(doctor__id=doctor_id).order_by(
                "-created"
            )

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
            PushNotification.objects.all().order_by("-created"),
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


from doctor.models import Appointments, Doctors
from accounts.models import User
from utilities.utils import time_localize


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
            appointments = (
                Appointments.objects.filter(doctor__user__id=doctor_id)
                .select_related("patient")
                .order_by("-created")
            )
            all_trans = Transactions.objects.all()
            appointments_headers = [
                "Name",
                "Phone#",
                "DOB",
                "Gender",
                "Paid Amount",
                "Pay Mode",
                "Transaction Id",
                "Scheduled Date",
                "Current Status",
                "Meeting Link",
            ]

            worksheet.append(appointments_headers)
            for appointment in appointments:
                transaction_data = all_trans.filter(appointment=appointment).first()
                row = [
                    appointment.patient.name,
                    appointment.patient.phone,
                    appointment.patient.dob.strftime("%b %d, %Y"),
                    appointment.patient.gender.capitalize(),
                    transaction_data.paid_amount if transaction_data else 0,
                    transaction_data.pay_mode if transaction_data else 0,
                    transaction_data.trans_id if transaction_data else 0,
                    time_localize(appointment.schedule_date).strftime("%b %d, %Y %I:%M %p"),
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
            worksheet.column_dimensions["G"].width = 10  # TRANS ID
            worksheet.column_dimensions["H"].width = 22  # SCHEDULE DATE
            worksheet.column_dimensions["I"].width = 18  # STATUS
            worksheet.column_dimensions["J"].width = 20  # MEETING LINK
            virtual_excel_file = save_virtual_workbook(workbook)
            response[
                "Content-Disposition"
            ] = f"attachment; filename={doctor_id}_appointment_report.xlsx"
            response.write(virtual_excel_file)

        # FINANCIAL REPORT
        elif action == "salary_and_payment_report":
            doctor_ids = request.GET.get("doctor_ids")
            all_appointmnets = Appointments.objects.all().order_by("-created")

            headers = [
                "Dr. NAME",
                "EMAIL",
                "PHONE",
                "Salary",
                "JAN",
                "FEB",
                "MAR",
                "APR",
                "MAY",
                "JUN",
                "JUL",
                "AUG",
                "SEP",
                "OCT",
                "NOV",
                "DEC",
            ]

            worksheet.append(headers)

            if doctor_ids:
                try:
                    doctor_ids = doctor_ids.split(",")
                    cleaned_list = [item for item in doctor_ids if str(item).strip()]
                    ids = [int(i) for i in cleaned_list]
                except:
                    return Response(
                        {
                            "status": False,
                            "message": "Please ensure that the IDs are provided as a comma-separated list of integers.",
                        },
                        400,
                    )

                Doctors_obj = Doctors.objects.select_related("user").filter(
                    user__id__in=ids
                )
            else:
                Doctors_obj = Doctors.objects.select_related("user").all()

            for doctor in Doctors_obj:
                row = [
                    doctor.user.get_full_name(),
                    doctor.user.email,
                    doctor.user.phone_number,
                    doctor.salary,

                    all_appointmnets.filter( # JANUARY
                        doctor__user=doctor.user,
                        schedule_date__month=1,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter( # FEBURARY
                        doctor__user=doctor.user,
                        schedule_date__month=2,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter( # MARCH
                        doctor__user=doctor.user,
                        schedule_date__month=3,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# APRIL
                        doctor__user=doctor.user,
                        schedule_date__month=4,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# MAY
                        doctor__user=doctor.user,
                        schedule_date__month=5,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# JUNE
                        doctor__user=doctor.user,
                        schedule_date__month=6,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# JULY
                        doctor__user=doctor.user,
                        schedule_date__month=7,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# AUGUST
                        doctor__user=doctor.user,
                        schedule_date__month=8,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# SEPTEMBER
                        doctor__user=doctor.user,
                        schedule_date__month=9,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# OCTOBER
                        doctor__user=doctor.user,
                        schedule_date__month=10,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# NOVEMBER
                        doctor__user=doctor.user,
                        schedule_date__month=11,
                        status="completed",
                    ).count(),

                    all_appointmnets.filter(# DECEMBER
                        doctor__user=doctor.user,
                        schedule_date__month=12,
                        status="completed",
                    ).count(),
                ]
                worksheet.append(row)

            worksheet.column_dimensions["A"].width = 15
            worksheet.column_dimensions["B"].width = 25
            worksheet.column_dimensions["C"].width = 15
            worksheet.column_dimensions["D"].width = 10

            worksheet.column_dimensions["E"].width = 5
            worksheet.column_dimensions["F"].width = 5
            worksheet.column_dimensions["G"].width = 5
            worksheet.column_dimensions["H"].width = 5
            worksheet.column_dimensions["I"].width = 5
            worksheet.column_dimensions["J"].width = 5
            worksheet.column_dimensions["K"].width = 5
            worksheet.column_dimensions["L"].width = 5
            worksheet.column_dimensions["M"].width = 5
            worksheet.column_dimensions["N"].width = 5
            worksheet.column_dimensions["O"].width = 5
            worksheet.column_dimensions["P"].width = 5

            virtual_excel_file = save_virtual_workbook(workbook)
            response[
                "Content-Disposition"
            ] = f"attachment; filename=salary_and_payment_report.xlsx"
            response.write(virtual_excel_file)

        return response


class AppointmentListView(AdminViewMixin):
    def get(self, request):
        status = request.GET.get("status")
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        query_set = (
            Appointments.objects.all()
            .select_related("doctor", "patient")
            .order_by("-created")
        )

        if status:
            status = str(status).lower()
            if status not in ["scheduled", "rescheduled", "completed"]:
                return Response(
                    {
                        "status": False,
                        "message": "This status is not recognized as valid in our system",
                    },
                    400,
                )
            query_set = query_set.filter(status=status)
            data = AppointmentsSerializer(query_set, many=True).data
            return Response({"status": True, "data": data}, 200)

        if from_date and to_date:
            if not is_valid_date(to_date, "%Y-%m-%d") and not is_valid_date(
                from_date, "%Y-%m-%d"
            ):
                return Response(
                    {"status": False, "message": "Provided date format is not valid"}
                )
            query_set = query_set.filter(
                initial_schedule_date__date__lte=to_date,
                initial_schedule_date__date__gte=from_date,
            )
            data = AppointmentsSerializer(query_set, many=True).data
            return Response({"status": True, "data": data}, 200)

        if from_date:
            if not is_valid_date(from_date, "%Y-%m-%d"):
                return Response(
                    {"status": False, "message": "Provided date format is not valid"}
                )
            query_set = query_set.filter(initial_schedule_date__date__gte=from_date)
            data = AppointmentsSerializer(query_set, many=True).data
            return Response({"status": True, "data": data}, 200)

        if to_date:
            if not is_valid_date(to_date, "%Y-%m-%d"):
                return Response(
                    {"status": False, "message": "Provided date format is not valid"}
                )
            query_set = query_set.filter(initial_schedule_date__date__lte=to_date)
            data = AppointmentsSerializer(query_set, many=True).data
            return Response({"status": True, "data": data}, 200)

        data = AppointmentsSerializer(query_set, many=True).data
        return Response({"status": True, "data": data}, 200)

    def put(self, request):
        """to change the status of appointment"""
        id = request.data.get("id")
        status = request.data.get("status")

        if not all([id, status]):
            return Response(
                {"status": False, "message": "Required values are missing"}, 400
            )

        try:
            app_obj = Appointments.objects.get(pk=id)
        except Exception as e:
            return Response(
                {"status": False, "message": "Appointment not found", "detail": str(e)},
                404,
            )

        try:
            app_obj.status = status
            app_obj.save()
            return Response(
                {"status": True, "message": "Appointment updated successfully"}, 200
            )
        except Exception as e:
            return Response(
                {"status": False, "message": "Something went wrong", "detail": str(e)}
            )


class SlotInfoView(AdminViewMixin):
    def get(self, request):
        Availabilities = Availability.objects.all()

        max_date = Availabilities.aggregate(max_date=Max("date"))["max_date"]
        min_date = Availabilities.aggregate(min_date=Min("date"))["min_date"]

        date_range = [
            min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)
        ]
        data_list = []
        for date in date_range:
            data_list.append(
                {
                    "date": date,
                    "is_available": Availabilities.filter(date=date).exists(),
                }
            )
        return Response({"status": True, "data": data_list})

    def post(self, request):
        day = request.data.get("day")
        try:
            if day:
                try:
                    day = int(day)
                except:
                    return Response(
                        {"status": False, "message": "day should be an integer"}
                    )
                response = UpdateSlot(day)
                DeleteSlot()
                return Response(
                    {
                        "status": True,
                        "message": f"Slots have been successfully updated for {response}.",
                    },
                    200,
                )
            response = UpdateSlot()
            DeleteSlot()
            return Response(
                {
                    "status": True,
                    "message": f"Slots have been successfully updated for {response}.",
                },
                200,
            )
        except Exception as e:
            return Response({"status": False, "message": str(e)}, 400)


class UserPaymentPriceView(AdminViewMixin):
    def get(self, request):
        user_payments = UserPaymentPrice.objects.order_by("-id")
        user_payments_data = UserPaymentPriceSerializer(user_payments, many=True).data
        return Response({"status": True, "data": user_payments_data})

    def post(self, request):
        price = request.data.get("price")
        if price is None:
            return Response({"status": False, "message": "Price is required"}, 400)

        if not isinstance(price, (float, int)):
            return Response(
                {
                    "status": False,
                    "message": "The price should be a floating-point or integer value",
                },
                400,
            )

        UserPaymentPrice.objects.create(price=price, created_by=request.user)
        return Response(
            {"status": True, "message": "Price has been successfully added"}, 201
        )


class AppointmentExport(AdminViewMixin):
    def post(self, request):
        status = request.data.get("status")
        from_date = request.data.get("from_date")
        to_date = request.data.get("to_date")

        query_set = (
            Appointments.objects.all()
            .select_related("doctor", "patient")
            .order_by("-created")
        )

        if status:
            status = str(status).lower()
            if status not in ["pending", "scheduled", "rescheduled", "completed", "cancelled", "expired"]:
                return Response(
                    {
                        "status": False,
                        "message": "This status is not recognized as valid in our system",
                    },
                    400,
                )
            query_set = query_set.filter(status=status)

        if from_date and to_date:
            if not is_valid_date(to_date, "%Y-%m-%d") and not is_valid_date(
                from_date, "%Y-%m-%d"
            ):
                return Response(
                    {"status": False, "message": "Provided date format is not valid"}
                )
            query_set = query_set.filter(
                initial_schedule_date__date__lte=to_date,
                initial_schedule_date__date__gte=from_date,
            )

        if from_date and not to_date:
            if not is_valid_date(from_date, "%Y-%m-%d"):
                return Response(
                    {"status": False, "message": "Provided date format is not valid"}
                )
            query_set = query_set.filter(initial_schedule_date__date__gte=from_date)

        if to_date and not from_date:
            if not is_valid_date(to_date, "%Y-%m-%d"):
                return Response(
                    {"status": False, "message": "Provided date format is not valid"}
                )
            query_set = query_set.filter(initial_schedule_date__date__lte=to_date)

        all_trans = Transactions.objects.all()
        headers = [
            "Patient Name",
            "Gender",
            "DOB",
            "Date & Time",
            "Doctor Name",
            "Email",
            "Mobile",
            "Status",
            "Paid Amount",
            "Pay Mode",
            "Trans ID",
            "Created",
        ]
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(headers)
        for appointment in query_set:
            transaction_data = all_trans.filter(appointment=appointment).first()
            row = [
                appointment.patient.name,
                appointment.patient.gender.capitalize(),
                appointment.patient.dob.strftime("%b %d, %Y"),
                appointment.schedule_date.strftime("%b %d, %Y %I:%M %p"),
                f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}",
                appointment.patient.email,
                appointment.patient.phone,
                appointment.status,
                transaction_data.paid_amount if transaction_data else "",
                transaction_data.pay_mode if transaction_data else "",
                transaction_data.trans_id if transaction_data else "",
                appointment.created.strftime("%b %d, %Y %I:%M %p"),
            ]
            worksheet.append(row)
        worksheet.column_dimensions["A"].width = 15  # Patient Name",
        worksheet.column_dimensions["B"].width = 10  # Gender",
        worksheet.column_dimensions["C"].width = 15  # DOB",
        worksheet.column_dimensions["D"].width = 22  # Date & Time",
        worksheet.column_dimensions["E"].width = 15  # Doctor Name",
        worksheet.column_dimensions["F"].width = 20  # Email",
        worksheet.column_dimensions["G"].width = 13  # Mobile",
        worksheet.column_dimensions["H"].width = 10  # Status",
        worksheet.column_dimensions["I"].width = 13  # Paid Amount",
        worksheet.column_dimensions["J"].width = 10  # Pay Mode",
        worksheet.column_dimensions["K"].width = 10  # Trans ID",
        worksheet.column_dimensions["L"].width = 22  # Created",
        virtual_excel_file = save_virtual_workbook(workbook)
        response[
            "Content-Disposition"
        ] = f"attachment; filename=appointment_report.xlsx"
        response["Content-Type"] = "application/octet-stream"
        response.write(virtual_excel_file)
        return response


class CancelAppointmentView(AdminViewMixin):
    def patch(self, request):
        appointment_id = request.data.get("appointment_id")
        if not appointment_id:
            return Response(
                {"status": False, "message": "Appointment id required"}, 400
            )

        try:
            appointment_obj = Appointments.objects.get(pk=appointment_id)
        except:
            return Response({"status": False, "message": "Appointment not found"}, 404)

        appointment_obj.status = "cancelled"
        appointment_obj.save()
        # Release assigned doctor
        avail_dr = Availability.objects.filter(
            doctor=appointment_obj.doctor, id=appointment_obj.slot_key
        ).first()
        avail_dr.is_booked = False
        avail_dr.save()

        return Response(
            {
                "status": True,
                "message": "Appointment has been successfully cancelled",
            },
            200,
        )
