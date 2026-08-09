from .models import sj_events, sj_users, sj_results
from django.db import transaction
from django.utils import timezone as django_timezone

import random
from random import seed
from random import randint

from datetime import *
from escpos.printer import Network, Dummy

import uuid
import time
from collections import defaultdict

# Import smtplib for sending email function
import smtplib, ssl

# Import the email modules we'll need
from email.message import EmailMessage

# ENV Settings (E-Mail)
from django.conf import settings

import logging
# Logging setup
logger = logging.getLogger('sj.logger')

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
    logger.debug(f"Kategorie berechnen, Gender: {u_gender}, u_byear: {u_byear}, u_age: {u_age}, event_year: {event_year}")
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
    logger.debug(f"Print-Templatename: { template }")
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
            logger.debug(f"Number of copies: {num_copies}")
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
        logger.error("Printing error:", type(error).__name__, "-", error)
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
    logger.debug(f'SEND-MAIL - Server: {settings.SMTP_SERVER}, Port: {settings.SMTP_PORT}, Sender: {settings.EMAIL_FROM}')
    logger.debug(f'SEND-MAIL - Bcc: {settings.EMAIL_BCC}, Subject: {msg_subj}')

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
    active_event = sj_events.objects.filter(event_active=True).order_by(
        '-updated_at',
        '-created_at',
        '-id',
    ).values(
        'id',
        'uuid',
        'event_name',
        'event_date',
        'event_location',
        'event_program',
        'event_reg_start',
        'event_reg_end',
        'event_reg_open',
        'event_num_lines'
    ).first()

    if datetime.now().date() <= active_event['event_reg_start'].date():
        reg_open = (False, "⏳ Voranmeldungen nehmen wir ab Anfang August entgegen.")

    elif active_event['event_reg_start'].date() <= datetime.now().date() <= active_event['event_reg_end'].date():
        reg_open = (True, "")
    else:
        reg_open = (False, "⏱️ Die online Registration ist zur Zeit geschlossen. Du kannst dich immer noch am Anlass vor Ort anmelden.")

    return {
            "id": active_event['id'],
            "uuid": active_event.get('uuid'),
            "name": active_event['event_name'],
            "date": active_event['event_date'],
            "location": active_event.get('event_location', ''),
            "event_program": active_event.get('event_program', ''),
            "reg_open": reg_open,
            "lines": active_event['event_num_lines']
            }


def reset_competition_data_with_three_events(event_num_lines=4):
    """
    Delete all results, users and events and create three events:
    - current year (active)
    - previous year (inactive)
    - two years ago (inactive)
    """
    current_year = django_timezone.now().year
    target_years = [current_year, current_year - 1, current_year - 2]

    with transaction.atomic():
        deleted_results, _ = sj_results.objects.all().delete()
        deleted_users, _ = sj_users.objects.all().delete()
        deleted_events, _ = sj_events.objects.all().delete()

        created_events = []
        for idx, year in enumerate(target_years):
            reg_start = django_timezone.make_aware(datetime(year, 1, 1, 0, 0, 0))
            reg_end = django_timezone.make_aware(datetime(year, 12, 31, 23, 59, 59))

            created_events.append(
                sj_events(
                    event_name=f"SJ Event {year}",
                    event_date=date(year, 8, 31),
                    event_location="Jegenstorf",
                    event_program="Sprint, Spiel, Jubel!",
                    event_active=(idx == 0),
                    event_reg_open=(idx == 0),
                    event_reg_start=reg_start,
                    event_reg_end=reg_end,
                    event_num_lines=event_num_lines,
                )
            )

        created_events = sj_events.objects.bulk_create(created_events)

    return {
        "deleted_results": deleted_results,
        "deleted_users": deleted_users,
        "deleted_events": deleted_events,
        "created_events": [
            {
                "id": event.id,
                "name": event.event_name,
                "year": event.event_date.year,
                "active": event.event_active,
            }
            for event in created_events
        ],
    }


def create_past_event_demo_results(event, max_users_per_category=8, finalists_per_category=4):
    """
    Create qualification and final results for one past event.
    Results are generated deterministically from event year/id.
    """
    users = list(
        sj_users.objects.filter(state='YES')
        .exclude(admin_state='deleted')
        .values('id', 'byear', 'gender')
    )

    if not users:
        return {
            'event_id': event.id,
            'event_name': event.event_name,
            'qualy_results_created': 0,
            'final_results_created': 0,
        }

    event_year = event.event_date.year
    lane_count = max(int(event.event_num_lines), 1)
    rng = random.Random(event_year * 1000 + event.id)

    users_per_category = defaultdict(list)
    for user in users:
        category = calc_cat(user['gender'], int(user['byear']), event_year)
        users_per_category[category].append(user)

    qualy_rows = []
    run_nr = 1

    for category in sorted(users_per_category.keys()):
        category_users = list(users_per_category[category])
        rng.shuffle(category_users)
        selected_users = category_users[:max_users_per_category]

        for idx, user in enumerate(selected_users):
            if idx > 0 and idx % lane_count == 0:
                run_nr += 1

            line_nr = (idx % lane_count) + 1
            qualy_time = round(9.2 + (idx % lane_count) * 0.25 + rng.uniform(0.0, 2.5), 2)

            qualy_rows.append(
                sj_results(
                    run_nr=run_nr,
                    line_nr=line_nr,
                    state='RQR',
                    result=qualy_time,
                    result_category=category,
                    fk_sj_users_id=user['id'],
                    fk_sj_events_id=event.id,
                )
            )

        run_nr += 1

    sj_results.objects.bulk_create(qualy_rows)

    best_per_category = defaultdict(list)
    for result in qualy_rows:
        best_per_category[result.result_category].append((result.fk_sj_users_id, result.result))

    final_rows = []
    final_run_nr = run_nr

    for category in sorted(best_per_category.keys()):
        ranked = sorted(best_per_category[category], key=lambda item: item[1])
        finalists = ranked[:finalists_per_category]

        for idx, (user_id, best_time) in enumerate(finalists):
            if idx > 0 and idx % lane_count == 0:
                final_run_nr += 1

            line_nr = (idx % lane_count) + 1
            final_time = round(max(0.01, best_time - rng.uniform(0.05, 0.30)), 2)

            final_rows.append(
                sj_results(
                    run_nr=final_run_nr,
                    line_nr=line_nr,
                    state='RFR',
                    result=final_time,
                    result_category=category,
                    fk_sj_users_id=user_id,
                    fk_sj_events_id=event.id,
                )
            )

        final_run_nr += 1

    sj_results.objects.bulk_create(final_rows)

    return {
        'event_id': event.id,
        'event_name': event.event_name,
        'qualy_results_created': len(qualy_rows),
        'final_results_created': len(final_rows),
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
        logger.info("Delete user -> No results, delete the user")
        user.delete()
    elif state == 'DEL':
        logger.info("Delete user -> Member has results, keep but clean it")
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
        logger.info("Delete user -> No action taken")

def generate_startnumber():
    seed()
    i = 1
    while i < 10:
        startngen = randint(100000, 999999)
        user_tst_startnr = sj_users.objects.filter(startnum=startngen)
        if len(user_tst_startnr) < 1:
            return startngen
        i += 1