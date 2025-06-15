import uuid
from django.db import models
from django.contrib import admin

# Create your models here.

# Teilnehmerinnen & Teilnehmer
# StartNummer unique=True
# Datenschutzerklärung akzeptiert
class sj_users(models.Model):
    GENDER = (
        ('W', 'weiblich'),
        ('M', 'männlich'),
    )

    STATE = (
        ('YES', 'Ich bin dabei'),
        ('NO', 'Ich kann diesmal leider nicht'),
        ('NOMAIL', 'Bitte nicht mehr einladen (keine E-Mails)'),
        ('DEL', 'Bitte meine Daten löschen'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    byear = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER)
    email = models.CharField(max_length=50, default='')
    phone = models.CharField(max_length=50, default='')
    city = models.CharField(max_length=50, default='')
    startnum = models.IntegerField(null=False, default=0)
    state = models.CharField(max_length=10, choices=STATE)
    admin_state = models.CharField(max_length=10, default='')

    def __str__(self):
        return f"{self.lastname}, {self.firstname}"

# Events
class sj_events(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_name = models.CharField(verbose_name="Anlass", max_length=50, null=False, default='')
    event_date = models.DateField(verbose_name="Datum")
    event_active = models.BooleanField(verbose_name="Event aktiv", default=False)
    #
    event_reg_open = models.BooleanField(verbose_name="Registration aktiv", default=False)
    event_reg_start = models.DateTimeField(verbose_name="Registration ab")
    event_reg_end = models.DateTimeField(verbose_name="Registration bis")
    #
    event_num_lines = models.IntegerField(verbose_name="Anzahl Bahnen", null=False, default=4)

    def __str__(self):
        return f"{self.event_name}"

# Resultate
class sj_results(models.Model):
    RESULT_STATE = (
        ('SQR', 'set for qualy run'),
        ('RQR', 'result qualy run'),
        ('SFR', 'set for final run'),
        ('RFR', 'result final run'),
        ('DNF', 'did not finish'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    fk_sj_users = models.ForeignKey(to="sj_users", on_delete=models.PROTECT)
    fk_sj_events = models.ForeignKey(to="sj_events", on_delete=models.PROTECT,)
    run_nr = models.IntegerField(verbose_name="Lauf Nr.", null=False, default=0)
    line_nr = models.IntegerField(verbose_name="Bahn", null=False, default=0)
    result = models.FloatField(verbose_name="Resultat", null=False, default=-1)
    result_category = models.CharField(verbose_name="Kategorie", null=False, default='', max_length=3)
    state = models.CharField(verbose_name="Status", max_length=3, null=False, choices=RESULT_STATE, default='DNF')

# Printer configuration
    # IP-Address, logo, paper (54mm, 80mm), what for (run, registration, ...)