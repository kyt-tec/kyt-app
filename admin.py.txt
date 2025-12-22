from django.contrib import admin
from .models import KYTSession
from .models import KYTSession, RiskEvaluation, Countermeasure, Participant

@admin.register(KYTSession)
class KYTSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'who', 'where', 'when', 'created_at')



admin.site.register(RiskEvaluation)
admin.site.register(Countermeasure)
admin.site.register(Participant)



