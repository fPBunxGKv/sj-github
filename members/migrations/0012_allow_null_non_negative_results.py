from django.db import migrations, models
from django.db.models import Q


def replace_missing_result_sentinel(apps, schema_editor):
    Result = apps.get_model('members', 'sj_results')
    Result.objects.filter(result__lt=0).update(result=None)


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0011_sj_events_event_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sj_results',
            name='result',
            field=models.FloatField(blank=True, default=None, null=True, verbose_name='Resultat'),
        ),
        migrations.RunPython(replace_missing_result_sentinel, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='sj_results',
            constraint=models.CheckConstraint(
                condition=Q(('result__isnull', True), _connector='OR') | Q(('result__gte', 0)),
                name='sj_results_result_non_negative',
            ),
        ),
    ]