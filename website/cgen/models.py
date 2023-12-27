from django.db import models, IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

import os
import hashlib

types = (
            ('tex', 'LaTeX Template'),
            ('svg', 'SVG Template'),
        )

# Create your models here.
def get_file_dir(instance, filename):
    if not  os.path.exists(settings.CERTIFICATES_PATH):
        os.mkdir(settings.CERTIFICATES_PATH)
    return os.sep.join(('certificates', str(instance.id), filename))

def get_certificate_dir(instance, filename):
    return os.sep.join(('certificates', str(instance.participant.certificate.id), str(instance.id), filename))

class Event(models.Model):
    """
        Event for which the participants claim certificate.
    """
    
    # Name of the Event
    name = models.CharField(max_length=1000)

    # Description for the event
    description = models.TextField()

    # Start date and time of the Event
    start_date = models.DateTimeField('Start date and time of the Event',
        default=timezone.now, null=True)

    # End date and time of the Event
    end_date = models.DateTimeField('End date and time of the Event',
        default=timezone.now, null=True)
    # Default set to infinite value


    # Published the event for the participants
    is_published = models.BooleanField(default=False)

    # One who creates the event (organiser)
    creator = models.ForeignKey(User, null=True, on_delete=models.PROTECT)


    def __str__(self):
        return self.name


class Certificate(models.Model):
    """
       Certificate for the participants
    """

    # Event to which the certificate belongs
    event = models.ForeignKey(Event, on_delete=models.PROTECT)

    # Type of certificate
    description = models.TextField()

    template_type = models.CharField(max_length=24, choices=types)

    # Template for the certificate 
    template = models.FileField(
            upload_to=get_file_dir,
            null=True, blank=True, default=None,
            help_text='Upload LaTeX template for the certificate'
        )
    background = models.FileField(
            upload_to=get_file_dir,
            null=True, blank=True, default=None,
            help_text='Upload background for the certificate in png or jpg',
        )
    variables = models.TextField()


    def __str__(self):
        return 'Certificate for {0}'.format(self.event.name)


class Participant(models.Model):

    email = models.EmailField(max_length=1000)

    certificate = models.ForeignKey('Certificate', on_delete=models.PROTECT)

    details = models.TextField()

    class Meta:
        unique_together = ['email', 'certificate']


    def __str__(self):
        return self.email



class CertificateManager(models.Model):

    certificate_file = models.FileField(
            upload_to=get_certificate_dir,
            null=True, blank=True, default=None,
        )

    participant = models.ForeignKey(Participant, on_delete=models.PROTECT)

    is_created = models.BooleanField(default=False)

    has_downloaded = models.BooleanField(default=False)

    certificate_creation_time = models.DateTimeField(default=timezone.now,
                                                     null=True)

    download_time  = models.DateTimeField(default=timezone.now)

    serial_key_long = models.CharField(unique=True, max_length=80,
                                       null=True, default=None)

    serial_key_short = models.CharField(unique=True, max_length=80,
                                        null=True, default=None)


    def __str__(self):
        return f"{self.participant.certificate.event} - {self.participant.email}"
    
    def generate_key(self, a = 0):
        email = self.participant.email
        certificate_id = self.participant.certificate.id
        if a != 0:
            s = f'{email}{certificate_id}{a}'
        else:
            s = f'{email}{certificate_id}'
        to_hash = bytes(s, 'utf-8')
        hashk = hashlib.sha1(to_hash).hexdigest()
        self.set_serial_key_long(hashk, a)
        return hashk

    def set_serial_key_long(self, key, a):
        try:
            self.serial_key_long = key
            self.save()
        except IntegrityError:
            a += 1
            self.generate_key(a)

    def set_serial_key_short(self, lkey, chars=4):
        try:
            self.serial_key_short = lkey[0:chars]
            self.save()
        except IntegrityError:
            chars += 1
            self.set_serial_key_short(lkey, chars)

    def get_serial_key_short(self):
        return self.serial_key_short


##############################################################################
