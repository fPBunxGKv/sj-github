import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from members.models import sj_users
from memers.sj_utils import get_event_info, sendmail

from members.tasks import send_invitation_email_task

# Logging setup
from django.conf import settings
logger = logging.getLogger('sj.logger')

# Utility to check if user is in admin group
def is_admin(user):
    return user.groups.filter(name='grp-admin').exists()

@login_required
@user_passes_test(is_admin)
def administration(request):
    if request.method == 'POST':
        if 'reset_admin_state' in request.POST:
            logger.info('Resetting admin_state ...')
            sj_users.objects.update(admin_state='')
            sj_users.objects.exclude(state__in=['DEL', 'NOMAIL']).update(state='')

        elif 'send_invitation_email' in request.POST:
            logger.info('Load event info ...')
            event_info = get_event_info()
            if not event_info:
                logger.error('No event information found.')
                return HttpResponse("No event information found.", status=500)

            logger.info('Sending invitation emails ...')
            user_emails = (
                sj_users.objects
                .filter(admin_state='', email__isnull=False)
                .exclude(state__in=['DEL', 'NOMAIL'])
                .values_list('email', flat=True)
                .distinct()
                .order_by('email')
            )

            for email in user_emails:
                # Queue the email task
                send_invitation_email_task.delay(email, event_info)

    context = {'pagetitle': 'SJ - Administration'}
    return render(request, 'administration_show.html', context)