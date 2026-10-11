import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_otp_sms(phone, otp):
    """
    Sends 6-digit OTP to phone number via Twilio SMS if credentials are configured.
    Falls back to console output in development / demo mode.
    Returns True if sent via real SMS, False otherwise.
    """
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')

    if account_sid and auth_token and from_number:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=f"Your StayEase verification code is: {otp}. Valid for 10 minutes.",
                from_=from_number,
                to=phone,
            )
            print(f"[SMS SUCCESS] Sent OTP {otp} to {phone} (SID: {message.sid})")
            return True
        except Exception as e:
            print(f"[SMS ERROR] Failed to send SMS via Twilio to {phone}: {e}")
            logger.error(f"Twilio SMS error: {e}")
            return False

    print(f"[DEMO SMS] OTP {otp} sent to {phone}")
    return False