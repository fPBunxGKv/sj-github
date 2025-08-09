import time
from datetime import datetime
import random
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from members.models import sj_users
from members.sj_utils import calc_cat

from fpdf import FlexTemplate, FPDF
import json

# Configure logging
logger = logging.getLogger('sj.logger')

@shared_task
def send_invitation_email_task(email, event_info):

    user_records = (sj_users.objects
        .filter(email=email)
        .exclude(state__in=['DEL', 'NOMAIL', 'YES'])
        .exclude(admin_state='EMAIL_SENT')
    )
    num_runners = user_records.count()

    ctx_body = {
        'num_runners': num_runners,
        'user_datasets': user_records,
        'event_info': event_info,
        'main_url': settings.MAIN_URL,
    }
    subject=f"Voranmeldung für den {event_info['name']}"

    # Render the email body HTML
    body_html = render_to_string('emails/invite_registation.html', ctx_body)

    # Strip HTML tags to create a plain text version of the email body.
    body_plain = strip_tags(body_html)

    # Then, create a multipart email instance.
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body_plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
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
        user_records.update(admin_state='EMAIL_ERROR')
        logger.exception(f"Error sending email to {email}: {e}")


@shared_task
def print_registered_users_task(event_info):
    """
    Task to print registered users.
    This is a placeholder for the actual printing logic.
    """
    logger.info("Printing registered users...")

    # Simulate a delay for printing
    time.sleep(2)
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # TODO: filepath via environment variable
    # Path to your JSON file
    json_file_path = "members/templates/printer/starting_coupons_a5.json"

    # Open and load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as infile:
        elements = json.load(infile)
    logger.info(f"Loaded JSON file: {json_file_path}")

    # Fetch all registered users
    users = sj_users.objects.filter(state='YES').exclude(admin_state='PRINTED').order_by('lastname', 'firstname')

    if not users:
        logger.info("Nothing to print")
        return
    pdf = FPDF()
    pdf.add_page(format="A5")
    f = FlexTemplate(pdf, elements)

    for user in users:
        result_category = calc_cat(user.gender, user.byear, event_info['date'].year)
        logger.info(f"Registered User: {user.firstname} {user.lastname}, Birth Year: {user.byear}, Category: {result_category}, Start Number: {user.startnum}")


        for i in [5,55,103]:
        # for i in [5]:
            f["logo"] = "members/static/logo_211x211.png"
            f["event_name"] = f"{event_info['name']}"
            f["firstname"] = f"Vorname: {user.firstname}"
            f["lastname"] = f"Name: {user.lastname}"
            f["byear"] = f"Jahrgang: {user.byear}"
            f["category"] = f"{result_category}"
            f["start_nr_bc"] = f"*{user.startnum}*"
            f["start_nr_str"] = f"{user.startnum}"
            f.render(offsetx=i, offsety=110, rotate=0.0, scale=1.0)

        pdf.set_line_width(0.1)
        pdf.line(x1=50, y1=110, x2=50, y2=190)
        pdf.line(x1=99, y1=110, x2=99, y2=190)
        
    pdf.add_page(same=True)

    pdf.output(f"data/{timestamp}_registered_users_a5.pdf")

    logger.info("Finished printing registered users.")