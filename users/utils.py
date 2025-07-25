import random
from django.core.mail import send_mail



def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(username, email, otp):
    subject = 'Your OTP for Password Reset'
    message = f"""
                Hi {username},

                We received a request to reset your password for your account associated with this email.

                Your One-Time Password (OTP) is:

                    {otp}

                Please enter this OTP in the password reset page to proceed. This OTP is valid for the next 10 
                    minutes.

                If you did not request a password reset, please ignore this email or contact support.

                Thank you,
                Backend Bolt Team
            """
    from_email = 'no-reply@teambolt.com'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    if send_mail:
        return True
    return False