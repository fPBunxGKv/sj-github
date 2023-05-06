from django.contrib import admin
from .models import *

class sj_eventsAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'event_date', 'event_active')
    search_fields = ('event_name',)
    list_filter = ('event_date',)


# Register your models here.
admin.site.register(sj_users)
admin.site.register(sj_events, sj_eventsAdmin)
admin.site.register(sj_results)