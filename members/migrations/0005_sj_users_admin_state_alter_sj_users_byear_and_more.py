# Generated by Django 4.2 on 2024-06-09 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_alter_sj_users_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='sj_users',
            name='admin_state',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='sj_users',
            name='byear',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sj_users',
            name='gender',
            field=models.CharField(choices=[('W', 'weiblich'), ('M', 'männlich')], max_length=1),
        ),
        migrations.AlterField(
            model_name='sj_users',
            name='state',
            field=models.CharField(choices=[('YES', 'Ich bin dabei'), ('NO', 'Ich kann diesmal leider nicht'), ('DEL', 'Bitte meine Daten löschen')], max_length=10),
        ),
    ]