from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.utils import timezone as django_timezone

from members.models import sj_events
from members.sj_utils import (
    create_past_event_demo_results,
    reset_competition_data_with_three_events,
)


class Command(BaseCommand):
    help = (
        "Delete all results/users/events, create 3 events "
        "(current year active + previous two years), and optionally load users fixture."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--users-fixture",
            default="sj_users_demo.json",
            help="Fixture file to load users from after reset (relative to project root).",
        )
        parser.add_argument(
            "--skip-users",
            action="store_true",
            help="Skip loading users fixture after event reset.",
        )
        parser.add_argument(
            "--skip-past-results",
            action="store_true",
            help="Skip generating qualification/final results for past events.",
        )

    def handle(self, *args, **options):
        summary = reset_competition_data_with_three_events()

        self.stdout.write(self.style.SUCCESS("Data reset completed:"))
        self.stdout.write(
            f"- Deleted result rows: {summary['deleted_results']}\n"
            f"- Deleted user rows: {summary['deleted_users']}\n"
            f"- Deleted event rows: {summary['deleted_events']}"
        )

        self.stdout.write(self.style.SUCCESS("Created events:"))
        for event in summary["created_events"]:
            active_marker = " (active)" if event["active"] else ""
            self.stdout.write(
                f"- [{event['id']}] {event['name']} ({event['year']}){active_marker}"
            )

        if options["skip_users"]:
            self.stdout.write("Skipped loading users fixture.")
            self.stdout.write("Past event result generation skipped because no users were loaded.")
            return

        fixture_name = options["users_fixture"]
        fixture_path = Path(settings.BASE_DIR) / fixture_name

        if not fixture_path.exists():
            self.stderr.write(
                self.style.WARNING(
                    f"Users fixture not found: {fixture_name}. "
                    "Events were reset, but users were not loaded."
                )
            )
            return

        call_command("loaddata", fixture_name)
        self.stdout.write(self.style.SUCCESS(f"Loaded users fixture: {fixture_name}"))

        if options["skip_past_results"]:
            self.stdout.write("Skipped past event result generation.")
            return

        current_year = django_timezone.now().year
        past_events = sj_events.objects.filter(event_date__year__lt=current_year).order_by('-event_date')

        self.stdout.write(self.style.SUCCESS("Generating past event runs/results:"))

        for event in past_events:
            event_summary = create_past_event_demo_results(event)
            self.stdout.write(
                f"- [{event_summary['event_id']}] {event_summary['event_name']}: "
                f"RQR={event_summary['qualy_results_created']}, "
                f"RFR={event_summary['final_results_created']}"
            )