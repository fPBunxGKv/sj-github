import uuid
from django.db import models
from django.contrib import admin

# Create your models here.

# Teilnehmerinnen & Teilnehmer
# StartNummer unique=True
# Datenschutzerklärung akzeptiert
class sj_users(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    byear = models.IntegerField(default=0)
    gender = models.CharField(max_length=1, default='')
    email = models.CharField(max_length=50, default='')
    phone = models.CharField(max_length=50, default='')
    city = models.CharField(max_length=50, default='')
    startnum = models.IntegerField(null=False, default=0)
    state = models.CharField(max_length=10, default='')

# Anlaesse
class sj_events(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_name = models.CharField(max_length=50, null=False, default='')
    event_date = models.DateTimeField()
    event_active = models.BooleanField(True,False, default=False)
    # 
    event_reg_open = models.BooleanField(True,False, default=False)
    event_reg_start = models.DateTimeField()
    event_reg_end = models.DateTimeField()
    # 
    event_num_lines = models.IntegerField(null=False, default=4)

# Resultate
class sj_results(models.Model):
    RESULT_STATE = (
        ('SQR', 'set for qualy run'),
        ('RQR', 'result qualy run'),
        ('SFN', 'set for final run'),
        ('RFN', 'result final run'),
        ('DNF', 'did not finish'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    fk_sj_users = models.ForeignKey("sj_users", on_delete=models.PROTECT)
    fk_sj_events = models.ForeignKey("sj_events", on_delete=models.PROTECT)
    run_nr = models.IntegerField(null=False, default=0)
    line_nr = models.IntegerField(null=False, default=0)
    result = models.FloatField(null=False, default=-1)
    result_category = models.CharField(null=False, default='', max_length=3)
    state = models.CharField(max_length=3, null=False, choices=RESULT_STATE, default='DNF')