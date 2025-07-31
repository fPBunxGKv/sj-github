import time
import random
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import sj_users

logger = logging.getLogger(__name__)

@shared_task
def send_invitation_email_task(email, event_info):
    # Add random delay between 1 and 5 seconds
    delay = random.uniform(1, 5)
    time.sleep(delay)

    user_records = sj_users.objects.filter(email=email)
    num_runners = user_records.count()

    ctx_body = {
        'num_runners': num_runners,
        'user_datasets': user_records,
        'event_info': event_info,
        'main_url': settings.MAIN_URL,
    }

    body_html = render_to_string('emails/invite_registation.html', ctx_body)

    try:
        send_state = send_mail(
            subject=f"Voranmeldung für den {event_info['name']}",
            message=strip_tags(body_html),
            recipient_list=[email],
            html_message=body_html,
            fail_silently=False,
            from_email=settings.DEFAULT_FROM_EMAIL,
        )
        if send_state:
            user_records.update(admin_state='EMAIL_SENT')
            logger.info(f'Email sent to: {email}')
        else:
            user_records.update(admin_state='EMAIL_FAILED')
            logger.warning(f'Email not sent to: {email}')
    except Exception as e:
        user_records.update(admin_state='EMAIL_FAILED')
        logger.exception(f"Failed to send email to {email}: {e}")
