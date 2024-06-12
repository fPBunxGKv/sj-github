from .models import sj_events, sj_users, sj_results

from random import seed
from random import randint

from datetime import *
from escpos.printer import Network, Dummy

import uuid

# Import smtplib for sending email function
import smtplib, ssl

# Import the email modules we'll need
from email.message import EmailMessage

# ENV Settings (E-Mail)
from django.conf import settings


def print_paper(user_data, run_time=0, printer_ip='172.20.30.170', template='default'):
    print(f"Print-Templatename: { template }")
    # test if logo file is present

    # init dummy printer
    d = Dummy()

    if template == 'run':
        # Font, align, etc. settings
        print(f"set_widh_default")
        d.set_with_default(align='center', font='a', bold=True, underline=0, width=2, height=2, density=9, invert=False, smooth=False, flip=False, double_width=False, double_height=False, custom_size=False)
        print(f"set_1")
        d.set(align='center', font='a', bold=True, width=2, height=2, density=9, double_width=True, double_height=True)

        # create ESC/POS for the print job, this should go really fast
        # d.ln(3)
        # d.image("static/logo_211x211.png")
        # d.ln(3)

        d.textln(user_data.fk_sj_users.firstname)
        d.textln(user_data.fk_sj_users.lastname)

        print(f"set_2")
        d.set(align='center', font='a', bold=True, width=2, height=2, density=9, double_width=False, double_height=False)
        d.textln(user_data.result_category)
        d.ln(1)

        if run_time > 0:
            d.text(f"--  {run_time:2.2f}  --\n")
        else:
            d.text(f"--  ERROR  --\n")

        d.ln(2)
        d.barcode(str(user_data.fk_sj_users.startnum), 'CODE39', height=80, width=2, pos='BELOW', font='A', align_ct=True, function_type=None, check=True, force_software=False)
        d.cut()

    elif template == 'register':
        d.text(f"Template: {template}\n")
        d.ln(2)
        d.cut()

    else:
        d.text(f"Template: {template}\n")
        d.text(f"Definition fehlt...\n")
        d.ln(2)
        d.cut()

    # send code to printer
    try:
        p = Network(host=printer_ip, timeout=1)
        p._raw(d.output)
        return True

    except Exception as error:
        print("Printing error:", type(error).__name__, "-", error)
        return False

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True, uuid.UUID(str(value))
    except ValueError:
        return False, ''

def sendmail(email='na', msg_subj='Subject', msg_body='Message Body Text', mail_format='html'):

    # print("Will send Email for:", value, state, firstname, email)
    # print(f'SEND-MAIL - Server: {settings.SMTP_SERVER}, Port: {settings.SMTP_PORT}, Sender: {settings.SENDER_EMAIL}')

    msg = EmailMessage()
    msg.set_content(msg_body)

    msg['From'] = f'{settings.EMAIL_FROM_DISPLAY_NAME} <{settings.EMAIL_FROM}>'
    msg['To'] = email
    msg['Bcc'] = f'{settings.EMAIL_BCC_DISPLAY_NAME} <{settings.EMAIL_BCC}>'
    msg['Subject'] = msg_subj

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(settings.SMTP_SERVER,settings.SMTP_PORT)
        server.starttls(context=context) # Secure the connection
        server.login(settings.EMAIL_FROM, settings.SMTP_PASSWORD)
        server.send_message(msg)
        send_success = True
    except Exception as e:
        # Print any error messages to stdout
        print(f'Exception in sendmail: {e}')
        send_success = False
    finally:
        server.quit()
        return send_success

def get_event_info():
    active_event = sj_events.objects.filter(event_active=True).values('id','event_name','event_date','event_reg_start','event_reg_end','event_reg_open','event_num_lines').first()

    if active_event['event_reg_start'].date() <= datetime.now().date() <= active_event['event_reg_end'].date():
        reg_open = True
    else:
        reg_open = False

    return {
            "id": active_event['id'],
            "name": active_event['event_name'],
            "date": active_event['event_date'],
            "reg_open": reg_open,
            "lines": active_event['event_num_lines']
            }

def delete_user(id):
    '''
    Delete all data of a user if he has no results in the database.
    Else just overwrite first/lastname with "***" and only keep ranking/result
    relevant values.
    Set state to DEL.
    '''
    user = sj_users.objects.get(id=id)

    if sj_results.objects.filter(fk_sj_users=user.id).count() < 1:
        print(" - No results, delete the user - ")
        user.delete()
    else:
        print(" - Member has results, keep but clean it - ")
        user.firstname = '***'
        user.lastname = '***'
        user.email = ''
        user.phone = ''
        user.city = ''
        user.state = 'DEL'
        user.save()

def generate_startnumber():
    seed()
    i = 1
    while i < 10:
        startngen = randint(100000, 999999)
        user_tst_startnr = sj_users.objects.filter(startnum=startngen)
        if len(user_tst_startnr) < 1:
            return startngen
        i += 1