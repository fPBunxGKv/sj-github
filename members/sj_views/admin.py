from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse

# ENV Settings (MAIN_URL)
from django.conf import settings

from members.models import sj_users

from ..sj_utils import get_event_info, sendmail


### administration
def is_admin(user):
    return user.groups.filter(name='grp-admin').exists()

@login_required 
@user_passes_test(is_admin)
def administration(request):

    if request.method == 'POST':
        if 'reset_admin_state' in request.POST:
            print(f'Clear admin_state ...')
            user_datasets = sj_users.objects.exclude(state='DEL').exclude(email='').values('email')
            user_datasets.update(admin_state='')

        elif 'send_invitation_email' in request.POST:
            print(f'Send Invitation Emails...')

            user_emails = sj_users.objects.filter(admin_state='').exclude(state='YES').exclude(state='DEL').exclude(email='').values('email').distinct().order_by('email')
            # print(user_emails.query)
            # print(f'Value-List: {user_emails.values_list}')

            # Load your template
            templ_body = loader.get_template('emails/invite_registation.html')

            for item in user_emails:
                user_datasets = sj_users.objects.filter(email=item['email']).exclude(state='YES').values()
                num_runners = user_datasets.count()

                ctx_body = {
                    'num_runners' : num_runners,
                    'user_datasets' : user_datasets,
                    'event_info': get_event_info(),
                    'main_url' : settings.MAIN_URL,
                    }
                
                # Render the template
                body_html = templ_body.render(ctx_body)

                print(f'--- {num_runners} -----------------------')
                print(body_html)
                subject = "Anmeldung"

                send_state = sendmail(item['email'], subject, body_html)

                # Set state to 'EMAILSENT'
                if send_state:
                    user_datasets.update(admin_state='EMAILSENT')
                else:
                    print(f'Email was not sent to: {item["email"]}')


    context = {
        'pagetitle' : 'SJ - Administration'
    }
    template = loader.get_template('administration_show.html')

    return HttpResponse(template.render(context, request))