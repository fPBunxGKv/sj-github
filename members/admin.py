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

# Register your models here.
admin.site.register(sj_users)
admin.site.register(sj_events, sj_eventsAdmin)
admin.site.register(sj_results)