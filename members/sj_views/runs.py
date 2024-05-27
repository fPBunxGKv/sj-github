from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from django.forms import Form, IntegerField

from django.db.models import Max, Min
from django.db.models import F, Window
from django.db.models.functions import Rank

from ..models import sj_users
from ..models import sj_events
from ..models import sj_results

from random import seed
from random import randint
from array import array

# Python imports
import random
from datetime import date

import logging

from ..sj_utils import get_event_info


logger = logging.getLogger(__name__)
debug_level = 1

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

# Wahr wenn doppelte Einträge in einem Array vorhanden sind
def test_dup_user(lines):
    contains_duplicates = False
    hold_single = []
    hold_double = []

    for num in lines:
        if num in hold_single:
            hold_double.append(num)
        elif num != 0:
            hold_single.append(num)

    if len(hold_double)>0:
        contains_duplicates = True

    return contains_duplicates

@login_required
def run(request):
    # Aktives event aus der DB lesen und anz. Bahnen / ID zurückgeben
    event_info = get_event_info()
    num_lines = event_info['lines']
    event_id = event_info['id']

    # Bereits erfasste Läufe abfragen, letzter gespeicherter Lauf ermitteln
    run_max = sj_results.objects.filter(fk_sj_events=event_id).aggregate(Max('run_nr'))

    runs_all_data = sj_results.objects.prefetch_related('fk_sj_events').filter(fk_sj_events=event_id).order_by('-run_nr','line_nr')

    template = loader.get_template('run.html')
    context = {
        'runs' : runs_all_data,
        'run_max' : run_max['run_nr__max'],
        'num_lines' : range(num_lines),
        'pagetitle' : 'SJ - Laufeinteilung',
    }
    return HttpResponse(template.render(context, request))


# --- ChatGPT ---
# ToDo: dynamisch auf Anzahl Bahnen (num_lines)
# Eine class für AddRunForm / EditRunForm (template muss auch angepasst werden)

class AddRunForm(Form):
    run_nr = IntegerField()
    addline1 = IntegerField(required=False)
    addline2 = IntegerField(required=False)
    addline3 = IntegerField(required=False)
    addline4 = IntegerField(required=False)
    addline5 = IntegerField(required=False)
    addline6 = IntegerField(required=False)
    addline7 = IntegerField(required=False)
    addline8 = IntegerField(required=False)

@login_required
def addrun(request):
    event_info = get_event_info()
    num_lines = event_info['lines']

    form = AddRunForm(request.POST or None)
    
    if form.is_valid():
        run_num = form.cleaned_data['run_nr']
        lines = [form.cleaned_data[f'addline{i+1}'] or 0 for i in range(num_lines)]
        print("Lines:",lines)

        # Prüfen auf doppelte Startnummer in einem Lauf
        if test_dup_user(lines):
            print('Doppelte Einträge in Laufeinteilung - Lauf wird nicht erfasst:', lines)

        else:
            users = sj_users.objects.filter(startnum__in=lines, state='YES')
            user_data = {user.startnum: (user.id, user.byear, user.gender) for user in users}
            print(user_data)

            results = []
            for i, startnum in enumerate(lines):
                if startnum != 0:
                    if startnum in user_data:
                        id, byear, gender = user_data[startnum]
                        result_category = calc_cat(gender, byear, event_info['date'].year)
                        results.append(sj_results(run_nr=run_num, line_nr=i+1, state='SQR', result_category=result_category, fk_sj_users_id=id, fk_sj_events_id=event_info['id']))

            sj_results.objects.bulk_create(results)

    return HttpResponseRedirect(reverse('run'))

@login_required
def editrun(request, id):
    event_info = get_event_info()
    num_lines = event_info['lines']

# nur zum editieren anzeigen falls noch keine Resulate vorhanden sind, sonst zurück auf Übersicht Zeiterfassung
    num_results_in_run = sj_results.objects.filter(run_nr=id, state = 'RQR').count()

    if (debug_level>=2): print('{} Resultate in Lauf Nummer {}'.format(num_results_in_run, id))

    if num_results_in_run > 0:
        return HttpResponseRedirect(reverse('run'))
    else:
        run_x_data = sj_results.objects.select_related().filter(run_nr=id)

        line_infos = {
            n: { } for n in range(1, int(num_lines) + 1)
        }

        for result in run_x_data:
            line_infos[result.line_nr] = {
                **result.__dict__,
                **result.fk_sj_users.__dict__
            }
            run_num = result.run_nr

        template = loader.get_template('run_edit.html')
        context = {
            'pagetitle' : 'SJ - Lauf bearbeiten',
            'num_lines' : range(1, int(num_lines) + 1),
            'run_num': run_num,
            'line_infos': line_infos,
        }
        return HttpResponse(template.render(context, request))

# --- ChatGPT ---
# ToDo: dynamisch auf Anzahl Bahnen (num_lines)
class UpdateRunForm(Form):
    run_num = IntegerField()
    edit_run1 = IntegerField(required=False)
    edit_run2 = IntegerField(required=False)
    edit_run3 = IntegerField(required=False)
    edit_run4 = IntegerField(required=False)
    edit_run5 = IntegerField(required=False)
    edit_run6 = IntegerField(required=False)
    edit_run7 = IntegerField(required=False)
    edit_run8 = IntegerField(required=False)

# --- ChatGPT optimiert updaterun---
@login_required
def updaterun(request):
    event_info = get_event_info()
    num_lines = event_info['lines']

    form = UpdateRunForm(request.POST or None)

    if form.is_valid():
        run_num = form.cleaned_data['run_num']
        lines = [form.cleaned_data[f'edit_run{i+1}'] or 0 for i in range(num_lines)]

        users = sj_users.objects.filter(startnum__in=lines, state='YES')
        user_data = {user.startnum: (user.id, user.byear, user.gender) for user in users}

        results = []

        # ToDo: Fehlermeldung zurückgeben
        if test_dup_user(lines):
            print('Doppelte Einträge in Laufeinteilung - Lauf wird nicht updated:', lines)

        else:
            # aktueller lauf löschen
            sj_results.objects.filter(run_nr=run_num).delete()

            for i, startnum in enumerate(lines):
                if startnum != 0:
                    if startnum in user_data:
                        id, byear, gender = user_data[startnum]
                        result_category = calc_cat(gender, byear, event_info['date'].year)
                        results.append(sj_results(run_nr=run_num, line_nr=i+1, state='SQR', result_category=result_category, fk_sj_users_id=id, fk_sj_events_id=event_info['id']))

            sj_results.objects.bulk_create(results)

        return HttpResponseRedirect(reverse('run'))

    return render(request, 'update_run.html', {'form': form})

# Close quali runs, prepare final runs
# delete qualificatin runs without results
# get rank 1-4 of each category and create runs (SFR, set final run)

@login_required
def set_final_runs(request):
    event_info = get_event_info()
    event_id = event_info['id']
    
    # delete qualificatin runs without results of the actua event
    sj_results.objects.filter(state='SQR', fk_sj_events=event_id).delete()

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
    
    top_n_results_per_cat = []

    for q in dist_cat:

        # Query Resultate pro Kategorie
        result_best_cat=sj_results.objects.filter(
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
                # 'result_category',
                # 'fast_run'
                'rank'
            )
        
        # Ranglist pro Kategorie zu Array hinzufügen
        num_finalists = result_best_cat.filter(rank__lte = 4).count()
        top_n_results_per_cat.extend(list(result_best_cat.filter(rank__lte = 4)))

        print(f'{5*"-"} {num_finalists} in cat {result_best_cat[0]["result_category"]} {5*"-"}')
        for n in result_best_cat.filter(rank__lte = 4):
            #print(n)
            print(f"{n['rank']:>2} {n['fk_sj_users__firstname']:<10} {n['fk_sj_users__lastname']:<10} {n['fast_run']:>5}")


    return HttpResponseRedirect(reverse('results'))


### add testdata
# ToDo: auf Admin Page einfügen und nur möglich falls beim aktuellen Event noch keine Laufeinteilung / Resultate vorhanden sind.
@login_required
def addrun_testdata(request, add_lines = 1):

    form = UpdateRunForm(request.POST or None)

    if form.is_valid():
        add_count_runs = form.cleaned_data['add_count_runs']
        print('Add result numbers:', add_count_runs )

    try:
        num_runs = add_lines
    except:
        num_runs = 1

    event_info = get_event_info()

    run_max = sj_results.objects.filter(fk_sj_events=event_info['id']).aggregate(Max('run_nr'))
    seed()

    if len(run_max) > 0 and run_max['run_nr__max']:
        run_max_1 = run_max['run_nr__max']
    else:
        run_max_1 = 1

    all_users = sj_users.objects.values('byear','gender','startnum')
    for i in range(run_max_1 + 1, num_runs + run_max_1 + 1):
        for j in range(1, event_info['lines'] + 1):
            start_index = randint(0, len(all_users)-1)

            # Kategorie erstellen
            # Uebergabe: Geschlecht, Geburtsjahr, Anlass-Jahr
            result_category = calc_cat(all_users[start_index]['gender'], int(all_users[start_index]['byear']), int(event_info['date'].strftime("%Y")))

            # Lauf mit Läufern in sj_results eintragen
            if (i + 2) < (num_runs + run_max_1 + 1):
                result_add_run = sj_results(run_nr = i,
                                            line_nr = j,
                                            state = 'RQR', # Set Result for qualification run
                                            result_category = result_category,
                                            fk_sj_users = sj_users.objects.get(startnum = all_users[start_index]['startnum']),
                                            fk_sj_events = sj_events.objects.get(event_active = True),
                                            result = round(random.uniform(9,12), 2),
                                            )
            else:
                result_add_run = sj_results(run_nr = i,
                                            line_nr = j,
                                            state = 'SQR', # Set for qualification run
                                            result_category = result_category,
                                            fk_sj_users = sj_users.objects.get(startnum = all_users[start_index]['startnum']),
                                            fk_sj_events = sj_events.objects.get(event_active = True),
                                            result = -1,
                                            )

            result_add_run.save()

    return HttpResponseRedirect(reverse('run'))
