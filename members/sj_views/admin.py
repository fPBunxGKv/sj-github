import logging
import random

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q

from members.models import sj_users
from members.sj_utils import get_event_info, sendmail

from members.tasks import print_registered_users_task, send_invitation_email_task

# Logging setup
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

        if 'send_invitation_email' in request.POST:
            logger.info('Load event info ...')
            event_info = get_event_info()
            if not event_info:
                logger.error('No event information found.')
                return HttpResponse("No event information found.", status=500)

            logger.info('Sending invitation emails ...')
            user_emails = (
                sj_users.objects
                .filter(
                    Q(admin_state='') | Q(admin_state__isnull=True),
                    email__isnull=False
                )
                .exclude(state__in=['DEL', 'NOMAIL', 'YES'])
                .values_list('email', flat=True)
                .distinct()
            )
            logger.info(f'Found {user_emails.count()} users to send emails to.')

            for i, email in enumerate(user_emails):
                jitter = random.randint(0, 2)
                total_delay = i + jitter
                # Queue the email task with a delay
                logger.info(f'Scheduling email to {email} with delay {total_delay} seconds.')
                send_invitation_email_task.apply_async(args=[email, event_info], countdown=total_delay)

        if 'print_registered_users' in request.POST:
            logger.info('Printing registered users ...')
            # Logic to print registered users
            event_info = get_event_info()
            print_registered_users_task.delay(event_info)

    context = {'pagetitle': 'SJ - Administration'}
    return render(request, 'administration_show.html', context)