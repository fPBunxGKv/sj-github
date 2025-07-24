import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from members.models import sj_users
from ..sj_utils import get_event_info, sendmail

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
            # Load event information
            event_info = get_event_info()
            if not event_info:
                logger.error('No event information found.')
                return HttpResponse("No event information found.", status=500)

            logger.info('Sending invitation emails ...')
            user_emails = (
                sj_users.objects
                .filter(admin_state='', email__isnull=False)
                .exclude(state__in=['DEL'])
                .values_list('email', flat=True)
                .distinct()
                .order_by('email')
            )

            for email in user_emails:
                user_records = (
                    sj_users.objects
                    .filter(email=email)
                )

                num_runners = user_records.count()

                ctx_body = {
                    'num_runners': num_runners,
                    'user_datasets': user_records,
                    'event_info': event_info,
                    'main_url': settings.MAIN_URL,
                }

                body_html = render_to_string('emails/invite_registation.html', ctx_body)

                send_state = send_mail(
                    subject=f"Voranmeldung für den {event_info['name']}",
                    message=strip_tags(body_html),  # plain text fallback
                    recipient_list=[email],
                    html_message=body_html,
                    fail_silently=False,  # Important!
                    from_email=settings.DEFAULT_FROM_EMAIL,
                )

                # Set state to 'EMAIL_SENT'
                if send_state:
                    user_records.update(admin_state='EMAIL_SENT')
                    logger.info(f'Email sent to: {email}')
                else:
                    user_records.update(admin_state='EMAIL_FAILED')
                    logger.warning(f'Email was not sent to: {email}')

    context = {'pagetitle': 'SJ - Administration'}
    return render(request, 'administration_show.html', context)
