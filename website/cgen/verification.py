from collections import OrderedDict

from cgen.models import CertificateManager


def verify(key):
    details = OrderedDict() 
    try:
        cm = CertificateManager.objects.get(serial_key_short=key)
        details['Authentic'] = True
        participant = cm.participant
        info = eval(participant.details)
        details['Event'] = participant.certificate.event.name
        description = participant.certificate.event.description
        details.update(info)
    except CertificateManager.DoesNotExist:
        details['Authentic'] = False
        return details, description
    return details, description


