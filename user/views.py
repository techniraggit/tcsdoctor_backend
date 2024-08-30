from utilities.utils import time_localize
import base64
from utilities.pigeon.service import send_email
from django.template.loader import render_to_string
from django.utils import timezone
import os
from django.conf import settings
from django.db import transaction
from doctor.models import (  # Doctor Models
    Users,
    Appointments,
    Availability,
    Transactions,
    Consultation,
)
from doctor.serializers import (  # Doctor Serializers
    AppointmentsSerializer,
    Patients,
    ConsultationSerializer,
)
from rest_framework.response import Response
from utilities.utils import (  # Utils
    is_valid_date,
    is_valid_email,
    is_valid_phone,
    get_room_no,
    generate_otp,
    generate_pdf,
    time_localize,
)
from core.decorators import token_required
from rest_framework.decorators import api_view
from administrator.models import UserPaymentPrice  # Admin models
from administrator.serializers import UserPaymentPriceSerializer  # Admin Serializers
from datetime import (  # Datetime
    datetime,
    timedelta,
)
from django.db.models import (
    F,
)

# Create your views here.
from .utils import Util

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

    parsed_date = datetime.strptime(date, "%Y-%m-%d").date()

    today = datetime.today().date()
    if not parsed_date >= today:
        return Response(
            {"status": False, "message": "The provided date is not valid."}, 400
        )

    current_date_time = datetime.now()

    if parsed_date == current_date_time.date():
        avail = (
            Availability.objects.filter(
                doctor__is_active=True,
                date=parsed_date,
                is_booked=False,
                time_slot__start_time__gt=current_date_time.time(),
            )
            .distinct()
            .order_by("time_slot__start_time")
            .annotate(slot_time=F("time_slot__start_time"))
            .values("slot_time")
        )
    else:
        avail = (
            Availability.objects.filter(
                doctor__is_active=True, date=parsed_date, is_booked=False
            )
            .distinct()
            .order_by("time_slot__start_time")
            .annotate(slot_time=F("time_slot__start_time"))
            .values("slot_time")
        )

    return Response({"status": True, "data": avail})


@token_required
@api_view(["POST"])
def schedule_meeting(request):
    if request.method == "POST":
        data = request.data

        user_required_fields = [
            "id",
            "first_name",
            "email",
            "phone_number",
        ]
        patient_required_fields = [
            "name",
            "phone",
            "email",
            "dob",
            "gender",
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

        patient_schedule_date = data["patient"].get("schedule_date")
        pre_health_issue = data["patient"].get("pre_health_issue", "").lower() == "yes"
        pre_health_issue_text = data["patient"].get("pre_health_issue_text")
        treatment_undergoing = (
            data["patient"].get("treatment_undergoing", "").lower() == "yes"
        )
        treatment_undergoing_text = data["patient"].get("treatment_undergoing_text")
        treatment_allergies = (
            data["patient"].get("treatment_allergies", "").lower() == "yes"
        )
        treatment_allergies_text = data["patient"].get("treatment_allergies_text")
        additional_note = data["patient"].get("additional_note")

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

        try:
            with transaction.atomic():
                users_obj, _ = Users.objects.get_or_create(user_id=user_id)

                users_obj.first_name = user_first_name
                users_obj.last_name = user_last_name
                users_obj.email = user_email
                users_obj.phone_number = user_phone_number
                users_obj.save()

                patient_obj, _ = Patients.objects.get_or_create(
                    user=users_obj,
                    name=patient_name,
                    dob=patient_dob,
                    gender=patient_gender,
                )
                patient_obj.phone = patient_phone
                patient_obj.email = patient_email
                patient_obj.save()

                schedule_date_obj = datetime.strptime(
                    patient_schedule_date, "%Y-%m-%d %H:%M"
                )

                availability_obj = (
                    Availability.objects.select_for_update()
                    .filter(
                        doctor__is_active=True,
                        date=schedule_date_obj.date(),
                        time_slot__start_time=schedule_date_obj.time().strftime(
                            "%H:%M"
                        ),
                        is_booked=False,
                    )
                    .order_by("doctor__priority")
                    .first()
                )

                if not availability_obj:
                    return Response(
                        {
                            "status": False,
                            "message": "We couldn't find any available doctors. Please make another selection.",
                        },
                        400,
                    )

                appointment_obj = Appointments.objects.create(
                    patient=patient_obj,
                    doctor=availability_obj.doctor,
                    schedule_date=schedule_date_obj,
                    initial_schedule_date=schedule_date_obj,
                    slot_key=availability_obj.id,
                    room_name=get_room_no(),
                    free_meetings_count=settings.NO_COST_CONSULT,
                    pass_code=generate_otp(4),
                    pre_health_issue=pre_health_issue,
                    pre_health_issue_text=pre_health_issue_text,
                    treatment_undergoing=treatment_undergoing,
                    treatment_undergoing_text=treatment_undergoing_text,
                    treatment_allergies=treatment_allergies,
                    treatment_allergies_text=treatment_allergies_text,
                    additional_note=additional_note,
                )
                availability_obj.is_booked = True
                availability_obj.save()
                appointment_obj.save()

                data = {
                    "appointment_id": appointment_obj.appointment_id,
                    "patient": appointment_obj.patient.patient_id,
                    "doctor": appointment_obj.doctor.user.id,
                    "schedule_date": appointment_obj.schedule_date,
                    "initial_schedule_date": appointment_obj.initial_schedule_date,
                    "slot_key": appointment_obj.slot_key,
                    "room_name": appointment_obj.room_name,
                    "free_meetings_count": appointment_obj.free_meetings_count,
                    "status": appointment_obj.status,
                    "is_join": appointment_obj.is_join,
                    "meeting_url": f"{os.environ.get('TCS_USER_FRONTEND')}{appointment_obj.room_name}",
                }


                body = f"Your Video Meeting Scheduled for {os.environ.get('TCS_USER_FRONTEND')}{appointment_obj.room_name}"
                data_set = {
                    'subject': 'Video Meeting Scheduled',
                    'body': body,
                    'to_email': patient_email,
                }
                Util.send_email(data_set)

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
@api_view(["POST"])
def amount_payment(request):
    if request.method == "POST":
        trans_id = request.data.get("trans_id")
        pay_mode = request.data.get("pay_mode")
        paid_amount = request.data.get("paid_amount")
        appointment_id = request.data.get("appointment_id")
        if not all([trans_id, pay_mode, paid_amount, appointment_id]):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )

        try:
            with transaction.atomic():
                appointment_obj = Appointments.objects.get(
                    pk=appointment_id  # , payment_status="unpaid"
                )
                appointment_obj.status = "scheduled"
                appointment_obj.payment_status = "paid"
                trans_obj = Transactions.objects.create(
                    appointment=appointment_obj,
                    trans_id=trans_id,
                    paid_amount=paid_amount,
                    pay_mode=pay_mode,
                )
                appointment_obj.save()
                invoice_context = {
                    "patient_name": trans_obj.appointment.patient.name,
                    "patient_email": trans_obj.appointment.patient.email,
                    "patient_phone": trans_obj.appointment.patient.phone,
                    "invoice_number": trans_obj.trans_id,
                    "invoice_date": trans_obj.created,
                    "paid_amount": trans_obj.paid_amount,
                    "pay_mode": trans_obj.pay_mode,
                }

            pdf_file = generate_pdf(
                template_name="pdf/invoice.html", context_data=invoice_context
            )
            file_content = base64.b64encode(pdf_file).decode("utf-8")
            html_message = render_to_string(
                "email/invoice_content.html", context=invoice_context
            )

            send_email(
                subject=f"Invoice for Tele Optometry Consultation - {trans_obj.appointment.patient.name}",
                body=html_message,
                recipients=[trans_obj.appointment.patient.email],
                file_content=file_content,
                file_name=f"{trans_obj.appointment.appointment_id}_invoice.pdf",
            )

            return Response(
                {"status": True, "message": "Payment successfully done"}, 200
            )
        except Appointments.DoesNotExist or Appointments.MultipleObjectsReturned:
            return Response({"status": False, "message": "Appointment not found"}, 404)

        except Exception as e:
            return Response({"status": False, "message": f"{e}"}, 400)


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
        input_format = "%Y-%m-%d %H:%M"
        schedule_date_obj = datetime.strptime(datetime_str, input_format)
        try:
            with transaction.atomic():
                availability_obj = (
                    Availability.objects.select_for_update()
                    .filter(
                        doctor__is_active=True,
                        date=schedule_date_obj.date(),
                        time_slot__start_time=schedule_date_obj.time(),
                        is_booked=False,
                    )
                    .order_by("doctor__priority")
                    .first()
                )

                if not availability_obj:
                    return Response(
                        {
                            "status": False,
                            "message": "We couldn't find any available doctors. Please make another selection.",
                        },
                        400,
                    )
                try:
                    appointment_obj = Appointments.objects.get(pk=appointment_id)
                except:
                    return Response(
                        {
                            "status": False,
                            "message": "Appointment not found",
                            "error": str(e),
                        },
                        404,
                    )
                try:
                    if appointment_obj.payment_status != "paid":
                        return Response(
                            {
                                "status": False,
                                "message": "Payment pending for this appointment, please make payment and try again later",
                            },
                            400,
                        )

                    initial_schedule_date = time_localize(
                        appointment_obj.initial_schedule_date
                    )
                    current_date = time_localize(timezone.now())
                    date_difference = current_date - initial_schedule_date
                    if date_difference > timedelta(days=7):
                        return Response(
                            {
                                "status": False,
                                "message": "This appointment expired, You are not able to reschedule this appointment",
                            },
                            400,
                        )
                    if not appointment_obj.free_meetings_count > 0:
                        return Response(
                            {
                                "status": False,
                                "message": "You have reached the limit of free appointments.",
                            }
                        )

                    appointment_time_difference = time_localize(appointment_obj.schedule_date) - time_localize(timezone.now())
                    if not appointment_time_difference >= timedelta(minutes=30):
                        return Response(
                            {
                                "status": False,
                                "message": "Apologies, it's too late to reschedule the appointment. You can reschedule appointments up to 30 minutes before the scheduled time.",
                            }
                        )

                    if (appointment_obj.is_attend_by_user and appointment_obj.is_attend_by_doctor) or (appointment_obj.is_attend_by_doctor and not appointment_obj.is_attend_by_user):
                        # Release preassigned doctor
                        avail_dr = Availability.objects.filter(
                            doctor=appointment_obj.doctor, id=appointment_obj.slot_key
                        ).first()
                        avail_dr.is_booked = False
                        avail_dr.save()

                        appointment_obj.pk = None
                        appointment_obj.doctor = availability_obj.doctor
                        appointment_obj.schedule_date = schedule_date_obj
                        appointment_obj.slot_key = availability_obj.id
                        appointment_obj.status = "rescheduled"
                        appointment_obj.room_name = get_room_no()
                        appointment_obj.is_attend_by_user = False
                        appointment_obj.is_attend_by_doctor = False
                        appointment_obj.pass_code = generate_otp(4)
                        appointment_obj.free_meetings_count = (
                            appointment_obj.free_meetings_count - 1
                        )
                        appointment_obj.save()

                        availability_obj.is_booked = True
                        availability_obj.save()
                        appointment_obj_old = Appointments.objects.get(
                            pk=appointment_id
                        )
                        appointment_obj_old.free_meetings_count = 0
                        appointment_obj_old.save()
                        return Response(
                            {
                                "status": True,
                                "message": "Appointment has been successfully rescheduled",
                            },
                            200,
                        )

                    elif (appointment_obj.is_attend_by_user and not appointment_obj.is_attend_by_doctor):
                        # Release preassigned doctor
                        avail_dr = Availability.objects.filter(
                            doctor=appointment_obj.doctor, id=appointment_obj.slot_key
                        ).first()
                        avail_dr.is_booked = False
                        avail_dr.save()

                        appointment_obj.doctor = availability_obj.doctor
                        appointment_obj.schedule_date = schedule_date_obj
                        appointment_obj.slot_key = availability_obj.id
                        appointment_obj.status = "rescheduled"
                        appointment_obj.room_name = get_room_no()
                        appointment_obj.pass_code = generate_otp(4)
                        # appointment_obj.free_meetings_count = (
                        #     appointment_obj.free_meetings_count - 1
                        # )
                        appointment_obj.is_attend_by_user = False
                        appointment_obj.is_attend_by_doctor = False
                        appointment_obj.save()

                        availability_obj.is_booked = True
                        availability_obj.save()
                        return Response(
                            {
                                "status": True,
                                "message": "Appointment has been successfully rescheduled",
                            },
                            200,
                        )
                    else:
                        return Response(
                            {
                                "status": False,
                                "message": "You are not able to reschedule this appointment",
                            },
                            400,
                        )

                except Exception as e:
                    return Response(
                        {
                            "status": False,
                            "message": "Something went wrong",
                            "error": str(e),
                        },
                        400,
                    )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong. Please try again later",
                },
                400,
            )


@token_required
@api_view(["PATCH"])
def cancel_meeting(request):
    if request.method == "PATCH":
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


@token_required
@api_view(["GET"])
def my_appointments(request):
    id = request.GET.get("id")
    if not id:
        return Response(
            {"status": False, "message": "Required fields are missing"}, 400
        )

    appointment_obj = (
        Appointments.objects.filter(patient__user__user_id=id)
        .order_by("-created")
        .exclude(status="pending")
    )
    data = AppointmentsSerializer(appointment_obj, many=True).data
    prescription_query = Consultation.objects.filter(appointment__in=appointment_obj)
    prescription_data = ConsultationSerializer(
        prescription_query, many=True, fields=["prescription"]
    ).data
    return Response(
        {"status": True, "data": data, "presciption_data": prescription_data}, 200
    )


@token_required
@api_view(["GET"])
def my_prescriptions(request):
    appointment_id = request.GET.get("appointment_id")
    if not appointment_id:
        return Response(
            {"status": False, "message": "Required fields are missing"}, 400
        )

    prescription_query = Consultation.objects.filter(appointment__pk=appointment_id)
    prescription_data = ConsultationSerializer(prescription_query, many=True).data
    return Response({"status": True, "presciption_data": prescription_data}, 200)


@token_required
@api_view(["POST"])
def user_verification(request):
    if request.method == "POST":
        room_name = request.data.get("room_name")
        pass_code = request.data.get("pass_code")

        if not all([room_name, pass_code]):
            return Response(
                {"status": False, "message": "Required fields are missing"}, 400
            )

        try:
            Appointments_obj = Appointments.objects.get(room_name=room_name)
            if Appointments_obj.payment_status != "paid":
                return Response(
                    {"status": False, "message": "Meeting payment is pending"}, 400
                )

            if Appointments_obj.pass_code == pass_code:
                data = {
                    "id": Appointments_obj.pk,
                    "schedule_date": time_localize(Appointments_obj.schedule_date),
                }
                return Response(
                    {
                        "status": True,
                        "message": "User authenticated successfully",
                        "data": data,
                    },
                    200,
                )
            return Response(
                {"status": False, "message": "Invalid provided passcode"}, 401
            )

        except Appointments.DoesNotExist or Appointments.MultipleObjectsReturned:
            return Response({"status": False, "message": "Meeting not found"}, 404)

        except Exception as e:
            return Response({"status": False, "message": str(e)}, 400)


@token_required
@api_view(["GET"])
def user_payment_price(request):
    prices = UserPaymentPrice.objects.order_by("-id").first()
    data = UserPaymentPriceSerializer(prices, fields=["price"]).data
    return Response({"status": True, "data": data}, 200)


@token_required
@api_view(["GET"])
def validate_call_user(request):
    room_name = request.GET.get("room_name")
    if not room_name:
        return Response({"status": False, "message": "room name required"}, 400)
    try:
        Appointments_obj = Appointments.objects.get(room_name=room_name)
        Appointments_obj.is_attend_by_user = True
        Appointments_obj.save()
        return Response({"status": True, "message": "updated successfully"}, 200)
    except:
        return Response({"status": False, "message": "Meeting not found"}, 404)
