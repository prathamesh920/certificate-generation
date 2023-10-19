from django.contrib import admin
from cgen.models import Event, Certificate, Participant, CertificateManager

# Register your models here.
admin.site.register(Event)
admin.site.register(Certificate)
admin.site.register(Participant)
admin.site.register(CertificateManager)
