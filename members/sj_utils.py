from .models import sj_events, sj_users, sj_results

from random import seed
from random import randint

from datetime import *
from escpos.printer import Network, Dummy

import uuid
import time

# Import smtplib for sending email function
import smtplib, ssl

# Import the email modules we'll need
from email.message import EmailMessage

# ENV Settings (E-Mail)
from django.conf import settings

def calc_cat(u_gender, u_byear, event_year):
    """ Berechnet die Kategorie

    Uebergabe:
        Geschlecht
        Geburtsjahr
        Anlass Jahr

        ToDo:
            - "Formel" in DB abbilden
            -
    """
    u_age = event_year - u_byear
    # print('Kategorie berechnen, Gender:', u_gender, 'u_byear:', u_byear, 'u_age:', u_age, 'event_year:', event_year)
    mstring = str(u_age)
    match mstring:
        case '0' | '1' | '2' | '3' | '4' | '5':
            cat_n =  '05'
        case '6':
            cat_n =  '06'
        case '7':
            cat_n =  '07'
        case '8':
            cat_n =  '08'
        case '9':
            cat_n =  '09'
        case '10':
            cat_n =  '10'
        case '11':
            cat_n =  '11'
        case '12' | '13':
            cat_n =  '12/13'
        case '14' | '15':
            cat_n =  '14/15'
        case _:
            cat_n =  '16/Open'
    return str(u_gender + cat_n)


def print_paper(user_data, run_time=0, printer_ip='172.20.30.170', template='default', num_copies=1, event_year=2020):
    print(f"Print-Templatename: { template }")
    # ToDo - test if logo file is present
    #        via dummy printer ?
    
    # init dummy printer
    # DumPrn = Dummy()

    try:
        

        if template == 'run':
            # DumPrn.ln(count=6)
            """
            Printer Model: TM-T88VI
            """
            # NetPrn = Network(host=printer_ip, timeout=1, profile='TM-T88VI')
            NetPrn = Network(host=printer_ip, timeout=1, profile='TM-T20II')
            # Empty lines
            NetPrn.set(align='center', font='a', bold=False, custom_size=True, width=3, height=1, density=1)
            NetPrn.textln(f'---')
            NetPrn.ln(count=5)
            NetPrn.textln(f'-            -')
            # Logo
            NetPrn.set(align='center')
            NetPrn.image("members/static/logo_211x211.png")
            NetPrn.ln(count=1)
            
            # Firstname
            NetPrn.set(align='center', font='a', bold=True, custom_size=True, width=2, height=2, density=8)
            NetPrn.textln(f'{user_data.fk_sj_users.firstname}')

            # Lastname
            NetPrn.set(align='center', font='a', bold=True, custom_size=True, width=1, height=1, density=8)
            NetPrn.textln(user_data.fk_sj_users.lastname)

            # Category
            NetPrn.ln(count=1)
            NetPrn.set(align='center', font='a', bold=True, custom_size=True, width=2, height=1, density=8)
            NetPrn.textln(user_data.result_category)
            
            # Result
            NetPrn.ln(count=1)
            if run_time > 0:
                NetPrn.set(align='center', font='a', bold=True, custom_size=True, width=2, height=2, density=8)
                NetPrn.textln(f"{run_time:2.2f}")
            else:
                NetPrn.set(align='center', font='a', bold=True, custom_size=True, width=2, height=2, density=8)
                NetPrn.textln(f"--  ERROR  --")

            # Startnumber as barcode inkl. text
            NetPrn.ln(count=2)
            # NetPrn.barcode(str(user_data.fk_sj_users.startnum), 'CODE39', height=80, width=2, pos='BELOW', font='a', align_ct=True, function_type=None, check=True, force_software=False)
            NetPrn.barcode(str(user_data.fk_sj_users.startnum), 'CODE39', height=80, width=2, pos='BELOW', font='a', align_ct=True, function_type=None, check=True)

            # Cut the paper & close the connection
            NetPrn.cut()
            NetPrn.close()

        elif template == 'register':
            """
            Printer Model: TM-T20II
            """
            NetPrn = Network(host=printer_ip, timeout=1, profile='TM-T20II')
            print_cat = calc_cat(user_data.gender, user_data.byear, event_year)
            print(f"Number of copies: {num_copies}")
            for n in range(num_copies):

                
                # Logo
                NetPrn.ln(count=6)
                NetPrn.set(align='center')
                NetPrn.image("members/static/logo_211x211.png")
                NetPrn.ln(count=1)
                
                # Firstname
                NetPrn.set(align='center', font='a', bold=True, custom_size=True, width=3, height=3, density=8)
                NetPrn.textln(f'{user_data.firstname}')

                # Lastname
                NetPrn.set(align='center', font='a', bold=False, custom_size=True, width=2, height=2, density=8)
                NetPrn.textln(user_data.lastname)

                # Category / Birthyear            
                NetPrn.ln(count=1)
                NetPrn.set(align='center', font='a', bold=True, custom_size=True, width=3, height=1, density=8)            
                NetPrn.textln(f'{user_data.byear}')
                NetPrn.textln(f'{print_cat}')

                # Startnumber as barcode inkl. text
                NetPrn.ln(count=2)
                # NetPrn.barcode(str(user_data.startnum), 'CODE39', height=90, width=3, pos='OFF', font='a', align_ct=True, function_type=None, check=True, force_software=False)
                NetPrn.barcode(str(user_data.startnum), 'CODE39', height=90, width=3, pos='OFF', font='a', align_ct=True, function_type=None, check=True)

                NetPrn.ln(count=1)
                NetPrn.set(align='center', font='a', bold=False, custom_size=True, width=2, height=2, density=8)
                NetPrn.textln(f'* {user_data.startnum} *')
                NetPrn.cut()
                NetPrn.close()

            return True

        else:
            NetPrn.text(f"Template: {template}\n")
            NetPrn.text(f"Definition fehlt...\n")
            NetPrn.ln(2)
            NetPrn.cut()

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

def delete_user(id, state='DEL'):
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
    elif state == 'DEL':
        print(" - Member has results, keep but clean it - ")
        user.firstname = '***'
        user.lastname = '***'
        user.email = ''
        user.phone = ''
        user.city = ''
        user.state = 'DEL'
        user.save()
    elif state == 'NOMAIL':
        user.email = ''
        user.phone = ''
        user.state = 'NOMAIL'
        user.save()
    else:
        print(" - No action taken - ")

def generate_startnumber():
    seed()
    i = 1
    while i < 10:
        startngen = randint(100000, 999999)
        user_tst_startnr = sj_users.objects.filter(startnum=startngen)
        if len(user_tst_startnr) < 1:
            return startngen
        i += 1