from django.contrib import admin
from .models import EscalationRule, EscalationLog

@admin.register(EscalationRule)
class EscalationRuleAdmin(admin.ModelAdmin):
    list_display = ('priority', 'resolution_deadline_hours', 'level1_warning_hours', 'escalation_level_2_target')

@admin.register(EscalationLog)
class EscalationLogAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'level', 'is_automated', 'triggered_by', 'triggered_at')
    list_filter = ('level', 'is_automated', 'triggered_at')
    search_fields = ('complaint__complaint_id', 'reason')
