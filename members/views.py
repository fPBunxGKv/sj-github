from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.conf import settings

from django.db.models import Min, Q
from django.db.models import Count

from django.db.models import F, Window
from django.db.models.functions import Rank

from .models import sj_users
from .models import sj_events
from .models import sj_results

from .forms import RegisterUserForm, UserForm

from random import seed
from random import randint
from array import array
from scipy.stats import rankdata

from .sj_views.runs import run, addrun, editrun, updaterun, set_final_runs, print_final_runs, addrun_testdata
from .sj_views.admin import administration

from datetime import *
# import uuid

from .sj_utils import print_paper, is_valid_uuid, sendmail, get_event_info, delete_user, generate_startnumber

import logging
# Logging setup
from django.conf import settings
logger = logging.getLogger('sj.logger')


# ---------- Pages ----------
def index(request):
    event_info = get_event_info()

    template = loader.get_template('index.html')
    context = {
        'event_info': event_info,
        'pagetitle' : 'SJ - Home'
    }
    return HttpResponse(template.render(context, request))

def register_new(request, id=''):
    event_info = get_event_info()

    if not event_info["reg_open"]:
        logger.info("Register NEW - Registration is closed")
        return HttpResponseRedirect(reverse('index'))

    isUUID, id = is_valid_uuid(id)
    logger.debug(f"Register NEW - isUUID: {isUUID}, uuid: {id}")
    
    if isUUID:
        '''
        If we get a valid UUID out of a string and userdata not with state "DEL",
        then redirect to django url with UUID
        else to an empty form.
        '''
        if sj_users.objects.filter(uuid=id).count() < 1:
            logger.info(f"Register NEW - Redirect to empty form, no user with UUID {id} found")
            return HttpResponseRedirect('/register/')

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = RegisterUserForm(request.POST or None)
        # check whether it's valid:
        if form.is_valid():
            # If we have a valid UUID with data -> update this record
            if isUUID:
                logger.info(f"Register NEW - Update record for UUID {id}")
                member = sj_users.objects.get(uuid=id)
                form = RegisterUserForm(request.POST, instance=member)
                form.save()
                # send status email to the user
                #sendmail(form.cleaned_data["state"], form.cleaned_data["firstname"], form.cleaned_data["email"], "Existing User")

            else:
                # Test if a user width the same "lastname, firstname, birthayear" exists -> then update this record

                user_exists = sj_users.objects.filter(
                    firstname = form.cleaned_data["firstname"],
                    lastname = form.cleaned_data["lastname"],
                    byear = form.cleaned_data["byear"],
                    gender = form.cleaned_data["gender"],
                    )
                if (user_exists.count()) >= 1:
                    member = sj_users.objects.get(uuid=user_exists[0].uuid)
                    form = RegisterUserForm(request.POST, instance=member)
                    form.save()
                else:
                    # add new user
                    # generate a unic startnumber
                    seed()
                    i = 1
                    while i < 10:
                        startngen = randint(100000, 999999)
                        user_tst_startnr = sj_users.objects.filter(startnum=startngen)
                        if len(user_tst_startnr) < 1:
                            obj = form.save(commit=False)
                            obj.startnum = startngen
                            obj.save()
                            break
                        i += 1

            ctx_body = {
                'state' : form.cleaned_data["state"],
                'firstname' : form.cleaned_data["firstname"],
                'form_data' : form.cleaned_data,
                'event_info': event_info,
                }

            # Generate email subject
            subject = None
            if form.cleaned_data["state"] == 'YES':
                subject = f'Anmeldebestätigung: {event_info["name"]}'
                messages.success(request, 'Wir haben deine Daten gespeichert. Du wirst in Kürze eine E-Mail mit der Anmeldebestätigung erhalten.')

            elif form.cleaned_data["state"] == 'NO':
                subject = f'{event_info["name"]}'
                messages.success(request, 'Wir haben deine Daten gespeichert. Wir hoffen dich nächstes Mal wieder zu sehen.')

            elif form.cleaned_data["state"] == 'DEL':
                subject = f'Konto gelöscht'
                messages.success(request, 'Wir haben deine Daten gelöscht. Du kannst dich jederzeit wieder anmelden.')
                delete_user(member.id)

            elif form.cleaned_data["state"] == 'NOMAIL':
                delete_user(member.id, state='NOMAIL')
                messages.success(request, 'Wir haben deine Email Adresse gelöscht. Du wirst in Zukunft keine E-Mails mehr erhalten.')

            if subject:
                email = form.cleaned_data["email"]
                # Render the email body HTML
                body_html = render_to_string('emails/confirm_registation.html', ctx_body)
                # Strip HTML tags to create a plain text version of the email body.
                body_plain = strip_tags(body_html)

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
                msg.send()

            # show thankyou page
            return HttpResponseRedirect(reverse('thankyou'))

    # if a GET (or any other method) we'll create a blank form
    else:
        if isUUID:
            '''
            If we get a valid UUID out of a string and userdata not with state "DEL",
            then redirect to django register url with UUID
            else to an empty form.
            '''
            if sj_users.objects.filter(uuid=id).count() > 0:
                logger.info(f"Register NEW - Found user with UUID {id}, loading data")
                member = sj_users.objects.get(uuid=id)

                # already registered
                if member.state == 'YES':
                    messages.success(request, 'Du bist bereits angemeldet!')
                    return HttpResponseRedirect(reverse('thankyou'))
                elif member.state != 'DEL':
                    logger.info(f"Register NEW - Loading form for user {member.firstname} {member.lastname}, State: {member.state}")
                    form = RegisterUserForm(instance=member, initial={'state': ''})
            else:
                form = RegisterUserForm()
                form = RegisterUserForm(initial={'state': 'YES'})
        else:
            form = RegisterUserForm()
            form = RegisterUserForm(initial={'state': 'YES'})

    context = {
        'pagetitle' : 'SJ - Anmeldung',
        'event_info': get_event_info(),
        'form' : form,
        }

    return render(request, "register_new.html", context)

def register_string(request, id):
    isUUID, id = is_valid_uuid(id)

    if isUUID:
        '''
        If we get a valid UUID out of a string and userdata not with state "DEL",
        then redirect to django registers url with UUID
        else to an empty form.
        '''
        if sj_users.objects.filter(uuid=id).count() > 0:
            member = sj_users.objects.get(uuid=id)
            if member.state != 'DEL':
                return HttpResponseRedirect('/register/'+ str(id))

    return HttpResponseRedirect('/register/')

def thankyou(request, state=''):
    logger.debug(f"IN view THANKYOU - {state}")
    event_info = get_event_info()

    template = loader.get_template('thankyou.html')
    context = {
        'event_info': event_info,
        'pagetitle' : 'SJ - Danke'
    }
    return HttpResponse(template.render(context, request))


@login_required
def users(request):
    # Fetch users with state != 'DEL' and order by firstname and lastname
    mymembers = sj_users.objects.exclude(state='DEL').exclude(admin_state='deleted').values().order_by('firstname', 'lastname')

    logger.debug(f"Users - begin, members count: {mymembers.count()}")

    searched = ""

    # Initialize the form
    form = UserForm(initial={'state': 'YES'})

    if request.method == 'POST':
        if 'clear' in request.POST:
            searched = ''
        else:
            searched = request.POST.get('query')

        if searched:
            mymembers = mymembers.filter(Q(firstname__icontains=searched) | Q(lastname__icontains=searched))
        if 'save' in request.POST:
            pk = request.POST.get('save')
            logger.debug(f"User {pk} - Save form")
            if int(pk) > 0:
                user = sj_users.objects.get(id=pk)
                form = UserForm(request.POST, instance=user)
            else:
                form = UserForm(request.POST or None)
            
            # check whether it's valid:
            if form.is_valid():
                obj = form.save(commit=False)

                # Generate a unique start number if not set
                if not obj.startnum:
                    logger.debug("No start number provided, generating a new one.")
                    obj.startnum = generate_startnumber()

                # Startzettel ausdrucken
                if obj.state == 'YES':
                    event_info = get_event_info()
                    event_year = event_info["date"].strftime("%Y")
                    prn_status = print_paper(user_data=obj, printer_ip=settings.PRINTER_REG_IP, template='register', num_copies=3, event_year=int(event_year))
                elif obj.state == 'NOMAIL':
                    prn_status = False
                    obj.email = ''
                    logger.debug(f"User {obj.firstname} {obj.lastname} email deleted: {obj.state}.")
                else:
                    logger.debug(f"User {obj.firstname} {obj.lastname} is not registered: {obj.state}.")
                    prn_status=False

                if prn_status:
                    logger.debug(f"Registration -> printed for {obj.firstname} {obj.lastname}")
                    obj.admin_state = "PRINTED"
                else:
                    logger.debug(f"Registration -> not printed: {prn_status}")
                    obj.admin_state = "NOT_PRINTED"

                obj.save()

                # initialize the empty form for a new user
                form = UserForm(initial={'state': 'YES'})

        elif 'print' in request.POST:
            pk = request.POST.get('print')
            user = sj_users.objects.get(id=pk)

            event_info = get_event_info()
            event_year = event_info["date"].strftime("%Y")

            logger.debug(f"User {user.firstname} {user.lastname} - Start print registration")
            prn_status = print_paper(user_data=user, printer_ip=settings.PRINTER_REG_IP, template='register', num_copies=3, event_year=int(event_year))

            if prn_status:
                logger.debug(f"Registration -> printed for {user.firstname} {user.lastname}")
                user.state = 'YES'
                user.admin_state = "PRINTED"
            else:
                logger.warning(f"Registration -> not printed for {user.firstname} {user.lastname}: {prn_status}")
                user.admin_state = "NOT_PRINTED"
            user.save()

        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            delete_user(pk)

        elif 'edit' in request.POST:
            pk = request.POST.get('edit')
            user = sj_users.objects.get(id=pk)

            # If the user is not deleted
            # then set the state to YES
            if user.state.upper() not in ['DEL', ]:
                user.state = 'YES'
                logger.debug(f'User {user.firstname} {user.lastname} - STATE {user.state} -> set to YES')

            form = UserForm(instance=user)

    template = loader.get_template('users_show.html')

    context = {
        'searched' : searched,
        'mymembers': mymembers,
        # 'page_obj': page_obj,
        'form': form,
        }

    return HttpResponse(template.render(context, request))


@login_required
def results(request):
    # DEBUG
    logger.debug('RESULTS -- request')

    # Aktives event aus der DB lesen und anz. Bahnen / ID zurückgeben
    event_info = get_event_info()
    num_lines = event_info['lines']
    event_id = event_info['id']

    # Bereits erfasste Läufe abfragen, letzter gespeicherter Lauf ermitteln
    runs_all_data = sj_results.objects.select_related().filter(fk_sj_events=event_id).order_by('-run_nr','line_nr')

    # DEBUG
    logger.debug(f"EVENT-ID: {event_id}, NUMBER-LINES: {num_lines}")

    template = loader.get_template('results_show.html')
    context = {
        'runs' : runs_all_data,
        'num_lines' : range(num_lines),
        'pagetitle' : 'SJ - Resultate',
    }
    return HttpResponse(template.render(context, request))

@login_required
def addresults(request, id):
    # DEBUG
    logger.debug(f'ADD-RESULTS --> request / ID: {id}')

    # Aktives event aus der DB lesen und anz. Bahnen / ID zurückgeben
    event_info = get_event_info()
    num_lines = event_info['lines']
    event_id = event_info['id']

    # Bereits erfasste Läufe abfragen, letzter gespeicherter Lauf ermitteln
    runs_all_data = sj_results.objects.select_related().filter(fk_sj_events=event_id,run_nr=id).order_by('-run_nr','line_nr')

    template = loader.get_template('results_add.html')
    context = {
        'runs' : runs_all_data,
        'num_lines' : range(num_lines),
        'pagetitle' : 'SJ - Resultate',
    }
    return HttpResponse(template.render(context, request))

@login_required
def saveresults(request):
    # DEBUG
    logger.debug('SAVE-RESULTS --> request')

    event_info = get_event_info()
    num_lines = event_info['lines']
    event_id = event_info['id']

    lines=array('f', [])
    lines = [0] * num_lines

    num = int(request.POST['run_num'])

    for i in range(num_lines):
        k = 'add_res' + str(i+1)

        try:
            raw = request.POST[k]
            lines[i] = float(raw)
        except:
            lines[i] = -1

        logger.debug(f'SAVE-RESULTS --> request, run-num = {num}, lines {i}: {lines[i]}')

        if lines[i] != -1:
            result_add_res = sj_results.objects.get(run_nr = num, line_nr = i+1, fk_sj_events = event_id)

            logger.debug(f'  --> resulte state: {result_add_res.state}')

            if (result_add_res.state == 'SQR') or (result_add_res.state == 'RQR'):
                previous_min = sj_results.objects.filter(fk_sj_users=result_add_res.fk_sj_users, fk_sj_events=event_id, result__gt=-1).aggregate(Min('result'))['result__min']
                logger.debug(f"{result_add_res.fk_sj_users}\n - Resulat Status: {result_add_res.state}\n - Event-ID: { event_id }\n - Bestzeit bisher: {previous_min}\n - neu Zeit: {lines[i]}")

                # Print or not (paper)
                if (previous_min == None):
                    logger.debug(" - Zettel für Wäscheleine drucken (none)!")
                    print_paper(user_data=result_add_res,  run_time=lines[i], template='run',printer_ip=settings.PRINTER_RUN_IP)
                elif (lines[i] < previous_min):
                    logger.debug(" - Zettel für Wäscheleine drucken (besser)!")
                    print_paper(user_data=result_add_res,  run_time=lines[i], template='run', printer_ip=settings.PRINTER_RUN_IP)
                else:
                    logger.debug(" - Leider keine neue Bestzeit!")

                # Set the sate for the result - used for ranking (qualy/final)
                result_add_res.state = 'RQR'

            elif (result_add_res.state == 'SFR') or (result_add_res.state == 'RFR'):
                # Set the sate for the result - used for ranking (qualy/final)
                result_add_res.state = 'RFR'
            else:
                logger.warning("!!! Resultat: Kein gültiger Status !!!")
                result_add_res.state = 'DNF'

            result_add_res.result = lines[i]
            result_add_res.save()

    return HttpResponseRedirect(reverse('results'))



# ### TeilnehmerIn löschen
# @login_required
# def delete(request, id):
#     '''
#     Delete all data of a user if they have no results in the database.
#     If there are results, anonymize personal information and set state to 'DEL'.
#     '''
#     try:
#         # Get the member by UUID
#         member = sj_users.objects.get(uuid=id)
#     except ObjectDoesNotExist:
#         logger.error(f"User with UUID {id} does not exist.")
#         return HttpResponseRedirect(reverse('users'))

#     # Check if user has any associated results
#     result_count = sj_results.objects.filter(fk_sj_users=member.id).count()

#     if result_count < 1:
#         # No results, proceed with deletion
#         logger.info(f"User {member.firstname} {member.lastname} with UUID {id} has no results. Deleting user.")
#         member.delete()
#     else:
#         # User has results, anonymize personal data
#         logger.info(f"User {member.firstname} {member.lastname} with UUID {id} has results. Anonymizing user data.")
#         member.firstname = '***'
#         member.lastname = '***'
#         member.email = ''
#         member.phone = ''
#         member.city = ''
#         member.state = 'DEL'
#         member.save()

#     return HttpResponseRedirect(reverse('users'))


def getResultsPerCategory(event_id, stateStr):
    '''
    Get results per categories from DB

    @type event_id: str
    @param event_id: event ID
    @type stateStr: str
    @param stateStr: Status of runs ('RQR' for first runs, 'RFR' for final runs)
    @rtype1: list, list of lists
    @returns: list of categories, list of categories containing a list of results ordered by fast run
    '''

    # Kategorien mit Resultaten auslesen
    dist_cat = sj_results.objects.filter(
            fk_sj_events=event_id,
            state=stateStr
            ).values(
                'result_category'
            ).distinct(

            ).order_by(
                'result_category'
            )

    # Resultate pro Kategorie -> Rangliste
    results_per_cat = []

    for q in dist_cat:
        # Query Resultate pro Kategorie
        result_best_cat=list(sj_results.objects.filter(
                fk_sj_events=event_id,
                state=stateStr,
                result_category=q['result_category'],
            ).values(
                'fk_sj_users',
                'fk_sj_users__firstname',
                'fk_sj_users__lastname',
                'result_category',
            ).annotate(
                fast_run=Min('result'),
                rank=Window(
                    expression=Rank(),
                    order_by=F('fast_run').asc()),
            ).order_by(
                'result_category',
                'fast_run'
            )
        )
        # Ranglist pro Kategorie zu Array hinzufügen
        results_per_cat.extend(result_best_cat)

    return dist_cat, results_per_cat

def getFirstRunningResultsPerCategory(event_id):
    return getResultsPerCategory(event_id, 'RQR')

def getFinalResultsPerCategory(event_id):
    return getResultsPerCategory(event_id, 'RFR')


# Rangliste
def ranking(request):

    # Aktives event aus der DB lesen und anz. Bahnen / ID zurückgeben
    event_info = get_event_info()
    event_id = event_info['id']

    # Query Resultate der Finalläufe
    fin_dist_cat, fin_results_per_cat = getFinalResultsPerCategory(event_id)

    # Query Resultate der Vorläufe
    dist_cat, results_per_cat = getFirstRunningResultsPerCategory(event_id)

    # Query Resultate über alle Kategorien
    result_best_all=list(sj_results.objects.filter(
            Q(state='RQR') | Q(state='RFR')
        ).filter(
            fk_sj_events=event_id
        ).values(
            'fk_sj_users',
            'fk_sj_users__firstname',
            'fk_sj_users__lastname',
            'result_category',
        ).annotate(
            fast_run=Min('result'),
            rank=Window(
                expression=Rank(),
                order_by=F('fast_run').asc()),
        ).order_by(
            'fast_run',
        )
    )

    context = {
        'pagetitle' : 'SJ - Rangliste',
        'event_info': event_info,
        'fin_results_per_cat' : fin_results_per_cat,
        'results_per_cat' : results_per_cat,
        'result_best_all' : result_best_all,
        'categories' : dist_cat,
        'fin_categories' : fin_dist_cat,
    }

    template = loader.get_template('rank_show.html')
    return HttpResponse(template.render(context, request))
