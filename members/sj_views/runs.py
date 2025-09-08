from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from django.forms import Form, IntegerField

from django.db.models import Max, Min
from django.db.models import F, Window
from django.db.models.functions import Rank
from django.db.models import Q

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
    event_id = event_info['id']

    debug_level = 3

    # nur zum editieren anzeigen falls noch keine Resulate vorhanden sind, sonst zurück auf Übersicht Zeiterfassung
    num_results_in_run = sj_results.objects.filter(run_nr=id, state='RQR', fk_sj_events_id=event_info['id']).count()

    num_results_in_run = sj_results.objects.filter(
        run_nr=id,
        fk_sj_events_id=event_info['id']
    ).filter(
        Q(state='RQR') | Q(state='RFR')
    ).count()

    if (debug_level>=2): print(f'{num_results_in_run} Resultate in Lauf Nummer {id} - Event > {event_info["name"]}')

    if num_results_in_run > 0:
        return HttpResponseRedirect(reverse('run'))
    else:
        run_x_data = sj_results.objects.select_related().filter(fk_sj_events=event_id).filter(run_nr=id)

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
    num_lines = event_info['lines']

    if request.method == 'POST':
        if 'delete-final' in request.POST:
            logger.info('Delete final runs')
            sj_results.objects.filter(state='SFR', result=-1.0, fk_sj_events=event_id).delete()
        elif 'generate-final' in request.POST:
            logger.info('Generate final runs')


            # delete qualification runs without results of the actual event
            sj_results.objects.filter(state='SQR', fk_sj_events=event_id).delete()
            sj_results.objects.filter(state='SFR', result=-1.0, fk_sj_events=event_id).delete()

            # get latest run number
            run_max = sj_results.objects.filter(fk_sj_events=event_id).aggregate(Max('run_nr'))
            run_next = run_max['run_nr__max'] + 1

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

            desired_order = [
                'W05', 'M05',
                'W06', 'M06',
                'W07', 'M07',
                'W08', 'M08',
                'W09', 'M09',
                'W10', 'M10',
                'W11', 'M11',
                'W12/13', 'M12/13',
                'W14/15', 'M14/15',
                'W16/Open', 'M16/Open'
                ]

            # Create order index map
            order_index = {value: index for index, value in enumerate(desired_order)}

            # Sort using the custom order
            dist_cat = sorted(
                dist_cat,
                key=lambda x: order_index.get(x['result_category'], len(order_index))
            )

            logger.debug(f'Distinct categories: {[d["result_category"] for d in dist_cat]}')

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

                # ToDo: define n in the event settings
                # Add best n per category to the final runs
                num_finalists = result_best_cat.filter(rank__lte = 4).count()
                top_n_results_per_cat.extend(list(result_best_cat.filter(rank__lte = 4)))

                final_runs = []
                print(f'\n{5*"-"} < {num_finalists} > in cat {result_best_cat[0]["result_category"]} {5*"-"}')

                for index, item in enumerate(list(result_best_cat.filter(rank__lte = 4))):
                    print(f"{item['rank']:>3}  {item['fk_sj_users__firstname']:<10} {item['fk_sj_users__lastname']:<10} {item['fast_run']:>5}")
                    # print(f"Vor if - Index: {index}, RunNext: {run_next}")
                    if (index > 0) and (index % num_lines == 0):
                        run_next += 1
                        line_nr = 1
                        # print(f"IN if - Index: {index}, RunNext: {run_next}")
                    else:
                        line_nr = (index % num_lines) + 1
                        # print(f"IN else - Index: {index}, RunNext: {run_next}, LineNr: {line_nr}")
                    final_runs.append(sj_results(run_nr=run_next, line_nr=line_nr, state='SFR', result_category=item['result_category'], fk_sj_users_id=item['fk_sj_users'], fk_sj_events_id=event_info['id']))

                sj_results.objects.bulk_create(final_runs)
                run_next += 1

    return HttpResponseRedirect(reverse('results'))

@login_required
def print_final_runs(request):
    # Aktives event aus der DB lesen und anz. Bahnen / ID zurückgeben
    event_info = get_event_info()
    num_lines = event_info['lines']
    event_id = event_info['id']

    desired_order = [
        'W05', 'W06', 'W07', 'W08', 'W09', 'W10', 'W11', 'W12/13', 'W14/15', 'W16/Open', # Women
        'PageBreak', # -> Add Page break in print_final_runs.html
        'M05', 'M06', 'M07', 'M08', 'M09', 'M10', 'M11', 'M12/13', 'M14/15', 'M16/Open', # Men
    ]

    final_runs_all_data = sj_results.objects.prefetch_related('fk_sj_events').filter(fk_sj_events=event_id, state='SFR').order_by('run_nr','line_nr')

    # Sort the list using the 'desired_order' list based on the 'result_category'
    final_runs_all_data_sorted = sorted(final_runs_all_data, key=lambda run: desired_order.index(run.result_category))

    template = loader.get_template('run_print_final.html')
    context = {
        'event_info' : event_info,
        'runs' : final_runs_all_data_sorted,
        'num_lines' : range(num_lines),
        'pagetitle' : 'SJ - Final-Laufeinteilung',
    }
    return HttpResponse(template.render(context, request))


### add testdata
# ToDo: Nur möglich falls beim aktuellen Event noch keine Laufeinteilung / Resultate vorhanden sind.
@login_required
def addrun_testdata(request, add_lines=1):
    form = UpdateRunForm(request.POST or None)
    
    if form.is_valid():
        add_lines = form.cleaned_data.get('add_count_runs', add_lines)
        logger.info(f'Add result numbers: {add_lines}')

    # Get event and current max run number
    event_info = get_event_info()
    event_id = event_info['id']
    event_year = int(event_info['date'].strftime("%Y"))
    lines_per_run = event_info['lines']

    current_max_run = (
        sj_results.objects
        .filter(fk_sj_events=event_id)
        .aggregate(Max('run_nr'))
        .get('run_nr__max') or 1
    )

    all_users = list(sj_users.objects.values('byear', 'gender', 'startnum'))
    total_runs_to_add = current_max_run + add_lines
    seed()

    active_event = sj_events.objects.get(event_active=True)

    for run_nr in range(current_max_run + 1, total_runs_to_add + 1):
        for line_nr in range(1, lines_per_run + 1):
            user_data = all_users[randint(0, len(all_users) - 1)]

            category = calc_cat(
                u_gender=user_data['gender'],
                u_byear=int(user_data['byear']),
                event_year=event_year
            )

            result_value = round(uniform(9, 12), 2) if (run_nr + 2) < (total_runs_to_add + 1) else -1
            result_state = 'RQR' if result_value != -1 else 'SQR'

            sj_results.objects.create(
                run_nr=run_nr,
                line_nr=line_nr,
                state=result_state,
                result_category=category,
                fk_sj_users=sj_users.objects.get(startnum=user_data['startnum']),
                fk_sj_events=active_event,
                result=result_value,
            )

    return redirect('run')
