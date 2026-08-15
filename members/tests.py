from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import sj_events, sj_results, sj_users
from .sj_utils import get_event_info


class AdministrationViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='admin', password='secret')
        self.group = Group.objects.create(name='grp-admin')
        self.user.groups.add(self.group)
        self.client.force_login(self.user)

        sj_users.objects.create(
            firstname='Alice',
            lastname='Example',
            email='alice@example.com',
            gender='W',
            byear=1990,
            state='NO',
            admin_state='',
        )
        sj_users.objects.create(
            firstname='Knall-Frosch',
            lastname='Example',
            email='knallfrosch@example.com',
            gender='W',
            byear=1990,
            state='NO',
            admin_state='EMAIL_SENT',
        )
        sj_users.objects.create(
            firstname='Bob',
            lastname='Example',
            email='bob@example.com',
            gender='M',
            byear=1990,
            state='YES',
            admin_state='',
        )
        sj_users.objects.create(
            firstname='Carol',
            lastname='Example',
            email='',
            gender='W',
            byear=1990,
            state='NO',
            admin_state='',
        )
        sj_users.objects.create(
            firstname='Dave',
            lastname='Example',
            email='dave@example.com',
            gender='M',
            byear=1990,
            state='DEL',
            admin_state='',
        )

    def test_show_invitation_recipients_lists_filtered_users(self):
        response = self.client.post(reverse('administration'), {'show_invitation_recipients': '1'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('invitation_recipients', response.context)
        self.assertEqual(len(response.context['invitation_recipients']), 1)
        self.assertContains(response, 'alice@example.com')
        self.assertNotContains(response, 'knallfrosch@example.com')
        self.assertNotContains(response, 'bob@example.com')
        self.assertNotContains(response, 'dave@example.com')


class EventInfoTests(TestCase):
    def test_editrun_handles_empty_run_without_crashing(self):
        self.user = get_user_model().objects.create_user(username='lane-editor', password='secret')
        self.client.force_login(self.user)

        sj_events.objects.create(
            event_name='Edit Empty Run Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_num_lines=4,
        )

        response = self.client.get(reverse('editrun', args=[42]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['run_num'], 42)
        self.assertEqual(len(response.context['line_infos']), 4)

    def test_editrun_redirects_when_run_has_rqr_or_rfr_results(self):
        self.user = get_user_model().objects.create_user(username='lane-editor-2', password='secret')
        self.client.force_login(self.user)

        event = sj_events.objects.create(
            event_name='Edit Redirect Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_num_lines=4,
        )

        participant = sj_users.objects.create(
            firstname='Redirect',
            lastname='Runner',
            email='redirect@example.com',
            gender='M',
            byear=1990,
            state='YES',
            startnum=700001,
        )

        sj_results.objects.create(
            fk_sj_users=participant,
            fk_sj_events=event,
            run_nr=81,
            line_nr=1,
            state='RQR',
            result_category='M05',
            result=10.2,
        )
        sj_results.objects.create(
            fk_sj_users=participant,
            fk_sj_events=event,
            run_nr=82,
            line_nr=1,
            state='RFR',
            result_category='M05',
            result=9.9,
        )

        response_rqr = self.client.get(reverse('editrun', args=[81]))
        response_rfr = self.client.get(reverse('editrun', args=[82]))

        self.assertEqual(response_rqr.status_code, 302)
        self.assertEqual(response_rqr.url, reverse('run'))
        self.assertEqual(response_rfr.status_code, 302)
        self.assertEqual(response_rfr.url, reverse('run'))

    def test_addrun_accepts_more_than_eight_lines(self):
        self.user = get_user_model().objects.create_user(username='lane-admin', password='secret')
        self.group = Group.objects.create(name='grp-lane-admin')
        self.user.groups.add(self.group)
        self.client.force_login(self.user)

        event = sj_events.objects.create(
            event_name='Many Lanes Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_num_lines=10,
        )

        for index in range(1, 11):
            sj_users.objects.create(
                firstname=f'Lane{index}',
                lastname='User',
                email=f'lane{index}@example.com',
                gender='M' if index % 2 else 'W',
                byear=1990,
                state='YES',
                startnum=600000 + index,
            )

        payload = {'run_nr': 1}
        payload.update({f'addline{index}': 600000 + index for index in range(1, 11)})

        response = self.client.post(reverse('addrun'), payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(sj_results.objects.filter(fk_sj_events=event).count(), 10)

    def test_addrun_testdata_respects_requested_run_count_and_excludes_del_users(self):
        self.user = get_user_model().objects.create_user(username='admin2', password='secret')
        self.group = Group.objects.create(name='grp-admin-2')
        self.user.groups.add(self.group)
        self.client.force_login(self.user)

        event = sj_events.objects.create(
            event_name='Test Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_num_lines=2,
        )

        active_user = sj_users.objects.create(
            firstname='Active',
            lastname='User',
            email='active@example.com',
            gender='M',
            byear=1990,
            state='YES',
            startnum=100001,
        )
        deleted_user = sj_users.objects.create(
            firstname='Deleted',
            lastname='User',
            email='deleted@example.com',
            gender='W',
            byear=1992,
            state='DEL',
            startnum=100002,
        )
        nomail_user = sj_users.objects.create(
            firstname='NoMail',
            lastname='User',
            email='',
            gender='M',
            byear=1994,
            state='YES',
            startnum=100003,
        )
        nostate_user = sj_users.objects.create(
            firstname='NoState',
            lastname='User',
            email='nostate@example.com',
            gender='W',
            byear=1996,
            state='NO',
            startnum=100004,
        )

        response = self.client.post(reverse('addtestdata'), {'add_count_runs': 3})

        self.assertEqual(response.status_code, 302)
        created_results = sj_results.objects.filter(fk_sj_events=event)
        self.assertEqual(created_results.count(), 6)
        self.assertTrue(created_results.filter(fk_sj_users=active_user).exists())
        self.assertFalse(created_results.filter(fk_sj_users=deleted_user).exists())
        self.assertTrue(created_results.filter(fk_sj_users=nomail_user).exists())
        self.assertFalse(created_results.filter(fk_sj_users=nostate_user).exists())

    def test_addrun_testdata_does_not_repeat_a_user_within_one_run(self):
        self.user = get_user_model().objects.create_user(username='admin3', password='secret')
        self.group = Group.objects.create(name='grp-admin-3')
        self.user.groups.add(self.group)
        self.client.force_login(self.user)

        event = sj_events.objects.create(
            event_name='Repeat Test Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_num_lines=2,
        )

        participant = sj_users.objects.create(
            firstname='Solo',
            lastname='Runner',
            email='solo@example.com',
            gender='M',
            byear=1990,
            state='YES',
            startnum=200001,
        )

        response = self.client.post(reverse('addtestdata'), {'add_count_runs': 1})

        self.assertEqual(response.status_code, 302)
        created_results = sj_results.objects.filter(fk_sj_events=event)
        self.assertEqual(created_results.count(), 1)
        self.assertEqual(created_results.first().fk_sj_users, participant)

    def test_addrun_testdata_limits_each_user_to_three_runs_per_event(self):
        self.user = get_user_model().objects.create_user(username='admin4', password='secret')
        self.group = Group.objects.create(name='grp-admin-4')
        self.user.groups.add(self.group)
        self.client.force_login(self.user)

        event = sj_events.objects.create(
            event_name='Cap Test Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_num_lines=2,
        )

        participant = sj_users.objects.create(
            firstname='Cap',
            lastname='Runner',
            email='cap@example.com',
            gender='M',
            byear=1990,
            state='YES',
            startnum=300001,
        )

        other_participant = sj_users.objects.create(
            firstname='Second',
            lastname='Runner',
            email='second@example.com',
            gender='W',
            byear=1992,
            state='YES',
            startnum=300002,
        )

        response = self.client.post(reverse('addtestdata'), {'add_count_runs': 4})

        self.assertEqual(response.status_code, 302)
        created_results = sj_results.objects.filter(fk_sj_events=event)
        participant_runs = created_results.filter(fk_sj_users=participant).count()
        other_runs = created_results.filter(fk_sj_users=other_participant).count()
        self.assertLessEqual(participant_runs, 3)
        self.assertLessEqual(other_runs, 3)

    def test_saveresults_redirects_back_with_sfr_filter(self):
        self.user = get_user_model().objects.create_user(username='admin5', password='secret')
        self.group = Group.objects.create(name='grp-admin-5')
        self.user.groups.add(self.group)
        self.client.force_login(self.user)

        event = sj_events.objects.create(
            event_name='Save Filter Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_num_lines=1,
        )

        result = sj_results.objects.create(
            fk_sj_users=sj_users.objects.create(
                firstname='Filter',
                lastname='User',
                email='filter@example.com',
                gender='M',
                byear=1990,
                state='YES',
                startnum=400001,
            ),
            fk_sj_events=event,
            run_nr=7,
            line_nr=1,
            state='SFR',
            result_category='M05',
            result=-1,
        )

        response = self.client.post(
            reverse('saveresults'),
            {'run_num': 7, 'add_res1': '10.5', 'state': 'SFR'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/results/?state=SFR')
        result.refresh_from_db()
        self.assertEqual(result.state, 'RFR')
        self.assertEqual(result.result, 10.5)

    def test_get_event_info_includes_location(self):
        sj_events.objects.create(
            event_name='Test Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_location='Berlin',
        )

        event_info = get_event_info()

        self.assertEqual(event_info['location'], 'Berlin')

    def test_download_calendar_returns_ics_content(self):
        response = self.client.get(
            reverse('download_calendar'),
            {
                'title': 'Test Event',
                'date': '2026-08-02',
                'location': 'Bern',
                'details': 'A test event',
            },
        )

        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/calendar', response['Content-Type'])
        self.assertIn('BEGIN:VCALENDAR', content)
        self.assertIn('SUMMARY:Test Event', content)
        self.assertIn('DTSTART:20260802T133000', content)
        self.assertIn('DTEND:20260802T180000', content)

    def test_download_calendar_uses_event_uuid_to_fetch_event_details(self):
        event = sj_events.objects.create(
            event_name='UUID Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_location='Zurich',
            event_program='Program line 1',
        )

        response = self.client.get(
            reverse('download_calendar'),
            {'event_uuid': str(event.uuid)},
        )

        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('SUMMARY:UUID Event', content)
        self.assertIn('LOCATION:Zurich', content)
        self.assertIn('DESCRIPTION:Program line 1', content)

    def test_download_calendar_encodes_umlauts_in_filename(self):
        response = self.client.get(
            reverse('download_calendar'),
            {
                'title': 'Münchenä Event',
                'date': '2026-08-02',
                'location': 'Bern',
                'details': 'A test event',
            },
        )

        self.assertIn("filename*=UTF-8''M%C3%BCnchen%C3%A4%20Event.ics", response['Content-Disposition'])

    def test_download_calendar_preserves_multiline_details(self):
        response = self.client.get(
            reverse('download_calendar'),
            {
                'title': 'Test Event',
                'date': '2026-08-02',
                'location': 'Bern',
                'details': 'First line\nSecond line\nThird line',
            },
        )

        content = response.content.decode('utf-8')

        self.assertIn('DESCRIPTION:First line\\nSecond line\\nThird line', content)

    def test_download_calendar_preserves_crlf_multiline_details(self):
        response = self.client.get(
            reverse('download_calendar'),
            {
                'title': 'Test Event',
                'date': '2026-08-02',
                'location': 'Bern',
                'details': 'First line\r\nSecond line\r\nThird line',
            },
        )

        content = response.content.decode('utf-8')

        self.assertIn('DESCRIPTION:First line\\nSecond line\\nThird line', content)
        self.assertNotIn('DESCRIPTION:First line\r', content)

    def test_ranking_export_csv_has_no_blank_lines_between_rows(self):
        self.user = get_user_model().objects.create_user(username='exporter', password='secret')
        self.client.force_login(self.user)

        event = sj_events.objects.create(
            event_name='Ranking Export Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_num_lines=4,
        )

        user_w = sj_users.objects.create(
            firstname='Wanda',
            lastname='Winner',
            email='wanda@example.com',
            gender='W',
            byear=2021,
            state='YES',
            startnum=800001,
        )
        user_w2 = sj_users.objects.create(
            firstname='Wanda',
            lastname='second first place',
            email='wanda2@example.com',
            gender='W',
            byear=2021,
            state='YES',
            startnum=800002,
        )
        user_m = sj_users.objects.create(
            firstname='Mark',
            lastname='Runner',
            email='mark@example.com',
            gender='M',
            byear=2021,
            state='YES',
            startnum=800003,
        )

        sj_results.objects.create(
            fk_sj_users=user_w,
            fk_sj_events=event,
            run_nr=1,
            line_nr=1,
            state='RFR',
            result_category='W05',
            result=10.11,
        )
        sj_results.objects.create(
            fk_sj_users=user_w2,
            fk_sj_events=event,
            run_nr=1,
            line_nr=2,
            state='RFR',
            result_category='W05',
            result=10.11,
        )
        sj_results.objects.create(
            fk_sj_users=user_m,
            fk_sj_events=event,
            run_nr=2,
            line_nr=1,
            state='RFR',
            result_category='M05',
            result=10.22,
        )

        response = self.client.get(reverse('ranking_export'))
        content = response.content.decode('utf-8-sig')
        lines = content.splitlines()

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertEqual(lines[0], 'Rang,Kategorie,Vorname,Nachname,Bestzeit')
        self.assertEqual(len(lines), 1 + 3)  # header + 3 results
        self.assertNotIn('', lines)
        categories = [row.split(',')[1] for row in lines[1:]]
        self.assertCountEqual(categories, ['W05', 'W05', 'M05'])

    def test_ranking_works_without_active_event_if_historical_event_has_results(self):
        event = sj_events.objects.create(
            event_name='Historical Results Event',
            event_date=timezone.now().date() - timedelta(days=30),
            event_reg_start=timezone.now() - timedelta(days=60),
            event_reg_end=timezone.now() - timedelta(days=31),
            event_active=False,
            event_num_lines=4,
        )

        participant = sj_users.objects.create(
            firstname='Hanna',
            lastname='History',
            email='hanna@example.com',
            gender='W',
            byear=2020,
            state='YES',
            startnum=810001,
        )

        sj_results.objects.create(
            fk_sj_users=participant,
            fk_sj_events=event,
            run_nr=1,
            line_nr=1,
            state='RFR',
            result_category='W05',
            result=9.87,
        )

        response = self.client.get(reverse('ranking'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Historical Results Event')

class AuthenticationTemplateTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.grp_admin = Group.objects.create(name='grp-admin')
        self.grp_kasse = Group.objects.create(name='grp-kasse')
        self.grp_lauf = Group.objects.create(name='grp-lauf')

        self.admin_user = get_user_model().objects.create_user(
            username='admin-user',
            password='secret',
            is_staff=True,
            is_superuser=True,
        )
        self.admin_user.groups.add(self.grp_admin)

        self.kasse_user = get_user_model().objects.create_user(
            username='kasse-user',
            password='secret',
        )
        self.kasse_user.groups.add(self.grp_kasse)

        self.lauf_user = get_user_model().objects.create_user(
            username='lauf-user',
            password='secret',
        )
        self.lauf_user.groups.add(self.grp_lauf)

    def test_login_form_renders_expected_fields(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, f'action="{self.login_url}"')
        self.assertContains(response, 'type="submit"')

    def test_admin_kasse_and_lauf_can_login_and_logout_with_nav_forms(self):
        for user in [self.admin_user, self.kasse_user, self.lauf_user]:
            with self.subTest(username=user.username):
                login_response = self.client.post(
                    self.login_url,
                    {'username': user.username, 'password': 'secret'},
                )

                self.assertEqual(login_response.status_code, 302)
                self.assertEqual(int(self.client.session['_auth_user_id']), user.id)
                authenticated_login_page = self.client.get(self.login_url)
                self.assertContains(authenticated_login_page, 'id="logout-form"')
                self.assertContains(authenticated_login_page, f'action="{self.logout_url}"')
                self.assertContains(authenticated_login_page, f'Logout ({user.username})')

                logout_response = self.client.post(self.logout_url)

                self.assertEqual(logout_response.status_code, 302)
                self.assertNotIn('_auth_user_id', self.client.session)

                anonymous_login_page = self.client.get(self.login_url)
                self.assertContains(anonymous_login_page, f'action="{self.login_url}"')
                self.assertNotContains(anonymous_login_page, 'id="logout-form"')

    def test_login_form_shows_error_for_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {'username': self.kasse_user.username, 'password': 'wrong-password'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Benutzername oder Passwort stimmen nicht.')
        self.assertNotIn('_auth_user_id', self.client.session)
