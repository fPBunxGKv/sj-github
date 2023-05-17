from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from django.db.models import Min
# from django.db.models import Max
from django.db.models import Count

from django.db.models import F, Window
from django.db.models.functions import Rank

from .models import sj_users
from .models import sj_events
from .models import sj_results

from .forms import RegisterUserForm

from random import seed
from random import randint
from array import array
from scipy.stats import rankdata

from .sj_views.runs import run, addrun, editrun, updaterun, addrun_testdata

# import random
from datetime import *
# import numpy as np


# ToDo: logging / debugging vereinheitlichen/verbessern

import logging
logger = logging.getLogger(__name__)

debug_level = 1

# ToDo: funktion doppelt (in views.py und in runs.py)
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
            # "reg_open": active_event['event_reg_open'],
            "lines": active_event['event_num_lines']
            }

def index(request):
    event_info = get_event_info()

    template = loader.get_template('index.html')
    context = {
        'event_info': event_info,
        'pagetitle' : 'SJ - Home'
    }
    return HttpResponse(template.render(context, request))

def register_new(request):
    # if this is a POST request we need to process the form data
    print('vor if post')
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = RegisterUserForm(request.POST or None)
        # check whether it's valid:
        if form.is_valid():
            firstname = form.cleaned_data["firstname"]
            lastname = form.cleaned_data["lastname"]

            print("Daten sind OK!", firstname, lastname)
            #form.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return render(request, "danke.html")
            # return HttpResponseRedirect("/thanks/")

        # if a GET (or any other method) we'll create a blank form
    else:
        print("Daten nicht OK!!!")
        form = RegisterUserForm()
        
    #template = loader.get_template('register_new_2.html')
    print(form.errors)

    context = {
        'pagetitle' : 'SJ - Anmeldung',
        'form' : form,
    }
    return render(request, "register_new_2.html", context)
    #return HttpResponse(template.render(context, request))



# def register_new(request):
#     template = loader.get_template('test_forms.html')
#     template = loader.get_template('register_new.html')
#     template = loader.get_template('register_new_2.html')
#     form = RegisterUserForm()
#     context = {
#         'pagetitle' : 'SJ - Anmeldung',
#         'form' : form
#     }
#     return HttpResponse(template.render(context, request))

def register_edit(request, id):
    if sj_users.objects.filter(uuid=id).count() > 0:

        member = sj_users.objects.get(uuid=id)
        if member.state != 'del':
            context = {
                'pagetitle' : 'SJ - Anmeldung Edit',
                'temprequest' : 'edit',
                'member': member,
            }

            template = loader.get_template('register_edit.html')
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect(reverse('register_new'))
    else:
        template = loader.get_template('register_new.html')
        context = {
            'pagetitle' : 'SJ - Anmeldung'
        }
        return HttpResponse(template.render(context, request))

@login_required
def users(request):
    mymembers = sj_users.objects.all().values().order_by('firstname','lastname')
    template = loader.get_template('users_show.html')
    context = {
        'mymembers': mymembers,
    }
    return HttpResponse(template.render(context, request))


@login_required
def results(request):
    # DEBUG
    if (debug_level >= 2): print('RESULTS -- request')

    # Aktives event aus der DB lesen und anz. Bahnen / ID zurückgeben
    event_info = get_event_info()
    num_lines = event_info['lines']
    event_id = event_info['id']

    # Bereits erfasste Läufe abfragen, letzter gespeicherter Lauf ermitteln
    runs_all_data = sj_results.objects.select_related().filter(fk_sj_events=event_id).order_by('-run_nr','line_nr')

    # DEBUG
    if (debug_level >= 2): print('EVENT-ID:', event_id,'\nNUMBER-LINES:', num_lines)

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
    if (debug_level >= 2): print('ADD-RESULTS --> request / ID:', id)
    # Aktives event aus der DB lesen und anz. Bahnen / ID zurückgeben
    active_event = sj_events.objects.filter(event_active=True).values('id', 'event_num_lines')
    event_id = active_event[0]['id']
    num_lines = active_event[0]['event_num_lines']

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
    if (debug_level >= 2): print('SAVE-RESULTS --> request')

    active_event = sj_events.objects.filter(event_active=True).values('id', 'event_num_lines')
    event_id = active_event[0]['id']

    #ToDo - NUMBER of Results per RUN.... Nicht num_lines
    num_lines = active_event[0]['event_num_lines']

    lines=array('f', [])
    lines = [0] * num_lines

    # for ll in request.POST:
    #     print(ll)

    num = int(request.POST['run_num'])
    for i in range(num_lines):
        k = 'add_res' + str(i+1)

        try:
            raw = request.POST[k]
            lines[i] = float(raw)
        except:
            lines[i] = -1

        if (debug_level >= 2): print('SAVE-RESULTS --> request, run-num =', num, ', lines', i, ':', lines[i])

        if lines[i] != -1:
            result_add_res = sj_results.objects.get(run_nr = num, line_nr = i+1)
            result_add_res.state = 'RQR'
            result_add_res.result = lines[i]
            result_add_res.save()

    return HttpResponseRedirect(reverse('results'))



### TeilnehmerIn erfassen
@login_required
def add(request):
    event_info = get_event_info()

    template = loader.get_template('add.html')
    context = {
        'pagetitle' : 'SJ - TeilnehmerIn hinzufügen',
        'event_info' : event_info,
    }
    return HttpResponse(template.render(context, request))

def addrecord(request):
    first = request.POST['fname']
    last = request.POST['lname']
    byear = request.POST['byear']
    gender = request.POST['gender']
    email = request.POST['uemail']
    phone = request.POST['phone']
    city = request.POST['city']
    state = request.POST['state']
    seed()
    i = 1
    while i < 3:
        startngen = randint(100000, 999999)
        member_tst_startnr = sj_users.objects.filter(startnum=startngen)
        if len(member_tst_startnr) < 1:
            member = sj_users(
                                firstname=first,
                                lastname=last,
                                byear=byear,
                                gender=gender,
                                email=email,
                                phone=phone,
                                city=city,
                                startnum=startngen,
                                state=state
                                )
            member.save()
            break
        i += 1

    return HttpResponseRedirect(reverse('index'))

@login_required
def delete(request, id):
    member = sj_users.objects.get(uuid=id)
    member.delete()
    return HttpResponseRedirect(reverse('index'))

@login_required
def edit(request, id):
    # ToDo: Gültigkeit prüfen
    #member = sj_users.objects.filter(uuid=id)
    member = sj_users.objects.get(uuid=id)
    #template = loader.get_template('edit.html')
    template = loader.get_template('add.html')
    if member.state != 'del':
        context = {
            'pagetitle' : 'SJ - TeilnehmerIn bearbeiten',
            'temprequest' : 'edit',
            'member': member,
        }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('add.html')
        context = {
            'pagetitle' : 'SJ - TeilnehmerIn hinzufügen',
        }
        return HttpResponse(template.render(context, request))

# ToDo: falls resultate vorhanden - Kategorie prüfen / updaten
'''
Benutzerdaten updaten
Update Userdata
'''
def updaterecord(request, id):
    fname = request.POST['fname']
    lname = request.POST['lname']
    byear = request.POST['byear']
    gender = request.POST['gender']
    email = request.POST['uemail']
    phone = request.POST['phone']
    city = request.POST['city']
    state = request.POST['state']

    member = sj_users.objects.get(uuid=id)

    member.firstname = fname
    member.lastname = lname
    member.byear = byear
    member.gender = gender
    member.email = email
    member.phone = phone
    member.city = city
    member.state = state

    member.save()
    return HttpResponseRedirect(reverse('users'))

# Rangliste
def ranking(request):
    # print('Ranking Request')
    active_event = sj_events.objects.filter(event_active=True).values('id', 'event_num_lines')
    event_id = active_event[0]['id']

# Kategorien mit Resultaten auslesen
    dist_cat = sj_results.objects.filter(
            fk_sj_events=event_id,
            state='RQR'
            ).values(
                'result_category'
            ).distinct(

            ).order_by(
                'result_category'
            )

    # DEBUG - Kategorien ausgeben
    if (debug_level >= 2):
        print('-'*20, 'category (disinct)','-'*20)
        for q in dist_cat:
            print(q)
        print('-'*20)

# Resultate pro Kategorie -> Rangliste
    results_per_cat = []

    for q in dist_cat:
        if (debug_level >= 2): print(' --- ',q['result_category'],' --- ')

    # Query Resultate pro Kategorie
        result_best_cat=list(sj_results.objects.filter(
                fk_sj_events=event_id,
                state='RQR',
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

        if (debug_level >= 2):
            for r in result_best_cat:
                print(r)
            print('-'*20)

# Query Resultate pro Kategorie
    result_best_all=list(sj_results.objects.filter(
            fk_sj_events=event_id,
            state='RQR',
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
        'results_per_cat' : results_per_cat,
        'result_best_all' : result_best_all,
        'categories' : dist_cat,
    }

    template = loader.get_template('rank_show.html')
    return HttpResponse(template.render(context, request))

### administration
@login_required
def administration(request):

    context = {
        'pagetitle' : 'SJ - Administration'
    }
    template = loader.get_template('administration_show.html')

    return HttpResponse(template.render(context, request))
