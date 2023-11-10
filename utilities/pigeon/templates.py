WELCOME = """
Your account at EyeMyEye has been successfully created!
You can log in and manage your profile at our website https://www.eyemyeye.com/
Regards,
EyeMyEye
"""

LOGIN_OTP = """
Hello {first_name},
Your one-time OTP for secure login is: {otp}.
Please use this OTP to complete your action. This OTP is valid for 5 minute.
If you didn't request this OTP, please ignore this message.
Regards,
EyeMyEye
"""

APPOINTMENT_BOOK_PATIENT = """
Dear {user_name},
Great news! Your appointment has been successfully booked.
Date: {appointment_date}
Time: {appointment_time}
PassCode: {pass_code}
click here to join meeting: {meeting_url}
Please review "My appointment" in your EYEMYEYE Login for appointment details.
We look forward to serving you.
Regards,
EyeMyEye
"""

APPOINTMENT_CANCEL_PATIENT = """
Dear {user_name},
We're sorry to hear that you've had to cancel your appointment.
Date: {appointment_date}
Time: {appointment_time}
If you wish to reschedule or have any questions,
please don't hesitate to reach out to us at.
We're here to assist you.
"""

APPOINTMENT_RESCHEDULE_PATIENT = """
Dear {user_name},
We understand that plans can change.
Your appointment has been successfully rescheduled to a new date and time.
Date: {appointment_date}
Time: {appointment_time}
PassCode: {pass_code}
click here to join meeting: {meeting_url}
Your updated appointment details are as follows.
If you have any questions or need further assistance,
please contact us at support email.
"""


APPOINTMENT_REMINDER_TITLE = "Reminder for upcoming Appointment "

APPOINTMENT_REMINDER_MESSAGE = """
A friendly reminder that your scheduled online appointment is just around the corner and will start shortly.
Date:{appointment_date}
Time:{appointment_time}
Please ensure you are prepared and have a stable internet
connection and any required materials ready.
If you have any last-minute questions or
need assistance, don't hesitate to
contact us at 97979-97979.
"""

APPOINTMENT_BOOK_DOCTOR_SUBJECT = "New Appointment Confirmation"
APPOINTMENT_BOOK_DOCTOR = """
Dear Dr. {dr_name},
We are pleased to inform you that a new appointment has been successfully booked for you at EyeMyEye.

Date: {appointment_date}
Time: {appointment_time}

Please ensure that you are prepared for the appointment. Make sure you have a stable internet connection and any required materials ready.
Thank you, and we look forward to your appointment.

Regards,
EyeMyEye

"""

APPOINTMENT_CANCEL_DOCTOR_SUBJECT = "Appointment Cancellation Notice"
APPOINTMENT_CANCEL_DOCTOR = """
Dear Dr. {dr_name},
We regret to inform you that your appointment scheduled for:

Date: {appointment_date}
Time: {appointment_time}

has been cancelled. If you have any questions or concerns, please don't hesitate to reach out to us at 97979797. We are here to assist you.
We apologize for any inconvenience this may have caused and appreciate your understanding.

Sincerely,
EyeMyEye

"""

APPOINTMENT_RESCHEDULE_DOCTOR_SUBJECT = "Updated Appointment Information"
APPOINTMENT_RESCHEDULE_DOCTOR = """
Dear Dr. {dr_name},
We understand that plans can change, and we wanted to inform you that your appointment has been rescheduled for the following time:

Date: {appointment_date}
Time: {appointment_time}

Please ensure that you are prepared for the appointment. Kindly check that you have a stable internet connection and any required materials ready.
If you have any questions or concerns about the rescheduled appointment, feel free to reach out.
Thank you for your understanding.

Sincerely,
EyeMyEye

"""