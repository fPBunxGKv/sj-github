# Generated by Django 4.2.1 on 2023-05-17 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_alter_sj_users_gender_alter_sj_users_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sj_users',
            name='state',
            field=models.CharField(choices=[('YES', 'Ich bin dabei'), ('NO', 'Ich kann diesmal leider nicht'), ('DEL', 'Bitte meine Daten löschen')], default='', max_length=10),
        ),
    ]