import logging
from django.core.mail import send_mail, mail_admins
from django.conf import settings
from django.contrib.auth import get_user_model
from adminpanel.models import Notification

logger = logging.getLogger(__name__)

def notify_admins(notif_type, message, link='', email_subject=None, email_body=None):
    """
    Creates a database Notification record for the admin panel,
    and optionally sends email notifications to administrators.
    """
    # 1. Create the database notification
    try:
        Notification.objects.create(
            notif_type=notif_type,
            message=message,
            link=link
        )
    except Exception as e:
        logger.error(f"Failed to create Notification database entry: {e}")

    # 2. Send email notification if subject and body are provided
    if email_subject and email_body:
        try:
            # Prepare recipient list from active staff/superusers with emails
            User = get_user_model()
            recipient_list = list(
                User.objects.filter(
                    is_active=True,
                    is_staff=True,
                    email__isnull=False
                ).exclude(email='').values_list('email', flat=True)
            )

            # Send using mail_admins (utilizing settings.ADMINS)
            if getattr(settings, 'ADMINS', None):
                mail_admins(
                    subject=email_subject,
                    message=email_body,
                    fail_silently=True
                )

            # Also send directly using send_mail to active staff users
            if recipient_list:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    fail_silently=True
                )
        except Exception as e:
            logger.error(f"Failed to send email notification to admins: {e}")
