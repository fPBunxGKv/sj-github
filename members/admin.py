from django.contrib import admin
from .models import *

class sj_eventsAdmin(admin.ModelAdmin):
    search_fields = ('event_name',)
    list_filter = ('event_date', 'event_active')

    list_display = ('event_name',
                    'event_date',
                    'event_active',
                    'event_reg_open',
                    'event_reg_start',
                    'event_reg_end',
                    )

    fieldsets = (
        (None, {
            'fields': ('event_name', 'event_date', 'event_active', 'event_num_lines')
        }),
        ('Registration', {
            'fields': ('event_reg_open', ('event_reg_start', 'event_reg_end'))
        }),
    )

class sj_resultsAdmin(admin.ModelAdmin):
    search_fields = ('fk_sj_users__lastname', 'fk_sj_users__firstname')
    list_filter = ('fk_sj_events', 'state',)

    list_display = (
            'fk_sj_users',
            'result_category',
            'result',
            'state',
            )



# Register your models here.
admin.site.register(sj_users)
admin.site.register(sj_events, sj_eventsAdmin)
admin.site.register(sj_results, sj_resultsAdmin)