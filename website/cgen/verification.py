from collections import OrderedDict

from cgen.models import CertificateManager


def verify(key):
    details = OrderedDict()
    description = None
    try:
        cm = CertificateManager.objects.get(serial_key_short=key)
        details['Authentic'] = True
        participant = cm.participant
        info = eval(participant.details)
        a = 'course'
        b = 'course1'
        c = 'course2'
        remove_course(a, info)
        remove_course(b, info)
        remove_course(c, info)
        details['Event'] = participant.certificate.event.name
        description = participant.certificate.event.description
        details.update(info)
    except CertificateManager.DoesNotExist:
        details['Authentic'] = False
        return details, description
    return details, description

def remove_course(i, d):
    if i in d:
        d.pop(i)
