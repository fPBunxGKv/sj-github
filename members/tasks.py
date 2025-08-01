import time
import random
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from members.models import sj_users

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

    # Render the email body HTML
    body_html = render_to_string('emails/invite_registation.html', ctx_body)
    
    # Strip HTML tags to create a plain text version of the email body.
    body_text = strip_tags(body_html)
    
    # Then, create a multipart email instance.
    msg = EmailMultiAlternatives(
        subject,
        body_plain,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        bcc=[settings.EMAIL_BCC],  # Bcc list
    )

    # Lastly, attach the HTML content to the email instance and send.
    msg.attach_alternative(body_html, "text/html")

    # If you want to log the email content for debugging, you can do so here
    logger.debug(f"Sending email to {email} with subject: {subject}")
    
    try:
        result = msg.send()
        if result:
            user_records.update(admin_state='EMAIL_SENT')
            logger.info(f"Email sent to {email}")
        else:
            user_records.update(admin_state='EMAIL_FAILED')
            logger.warning(f"Email not sent to {email}")
    except Exception as e:
        user_records.update(admin_state='EMAIL_FAILED')
        logger.exception(f"Error sending email to {email}: {e}")

    # try:
    #     send_state = send_mail(
    #         subject=f"Voranmeldung für den {event_info['name']}",
    #         message=strip_tags(body_html),
    #         recipient_list=[email],
    #         html_message=body_html,
    #         fail_silently=False,
    #         from_email=settings.DEFAULT_FROM_EMAIL,
    #         # bcc=[settings.EMAIL_BCC]
    #     )
    #     if send_state:
    #         user_records.update(admin_state='EMAIL_SENT')
    #         logger.info(f'Email sent to: {email}')
    #     else:
    #         user_records.update(admin_state='EMAIL_FAILED')
    #         logger.warning(f'Email not sent to: {email}')
    # except Exception as e:
    #     user_records.update(admin_state='EMAIL_FAILED')
    #     logger.exception(f"Failed to send email to {email}: {e}")
