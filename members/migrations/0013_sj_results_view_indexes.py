from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0012_allow_null_non_negative_results'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='sj_results',
            index=models.Index(
                fields=['fk_sj_events', 'run_nr', 'line_nr'],
                name='sj_result_event_run_line_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='sj_results',
            index=models.Index(
                fields=['fk_sj_events', 'state', 'result_category'],
                name='sj_result_event_state_cat_idx',
            ),
        ),
    ]