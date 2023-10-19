import os
import subprocess
from string import Template
import shutil

from pathlib import Path
from django.core.files import File
from django.conf import settings

from cgen.models import CertificateManager, Participant, Certificate


def get_certificate(certificate_id, email):
    try:
        participant = Participant.objects.get(email=email, certificate=certificate_id)
    except Participant.DoesNotExist:
        return (None, False)
    return  generate(certificate_id, email)

def get_details(certificate_id, email):
    certificate = Certificate.objects.get(id=certificate_id)
    participant = Participant.objects.get(email=email, certificate=certificate)
    certificate_details = {}
    cm, created = CertificateManager.objects.get_or_create(
                    participant=participant)
    key = cm.generate_key()
    #cm.set_serial_key_long(key)
    cm.set_serial_key_short(key)
    certificate_details['template'] = certificate.template.path
    certificate_details['template_type'] = certificate.template_type
    info = eval(f'{participant.details}')
    key = cm.get_serial_key_short()
    info['serial_key'] = key
    info['qr_code'] = f'https://fossee.in/certificates/verify/{key}/'
    certificate_details['info'] = info
    path = f'{settings.PATH}/{certificate.id}'
    certificate_details['path'] = path
    if not  os.path.exists(f"path/{{Makefile}}"):
        shutil.copy2(f'{settings.PATH}/Makefile', path)
    certificate_details['file_name'] = f'{email}-{certificate.id}'
    return cm, certificate_details


def generate(certificate, email):
    cm, certificate_details = get_details(certificate, email)
    template = certificate_details['template']
    info = certificate_details['info']
    path = certificate_details['path']
    file_name = certificate_details['file_name']
    template_type = certificate_details['template_type']
    msg = None
    has_error = False
    try:
        template_file = open(template, 'r')
        content = Template(template_file.read())
        template_file.close()
        if template_type == 'tex':
            content_tex = content.safe_substitute(info)
            create_tex = open('{0}/{1}.tex'.format(path, file_name), 'w')
            create_tex.write(content_tex)
            create_tex.close()
            return_value, msg = _make_certificate_certificate(path, file_name,
                                    command='participant_cert')
            if return_value == 0:
                path = Path('{0}/{1}.pdf'.format(path, file_name))
                with path.open(mode='rb') as f:
                    cm.certificate_file = File(f, name=path.name)
                    cm.save()
            else:
                has_error = True
        if template_type == 'svg':
            content_svg = content.safe_substitute(info)
            create_svg = open('{0}/{1}.svg'.format(path, file_name), 'w')
            create_svg.write(content_svg)
            create_svg.close()
            return_value, msg = _make_certificate_certificate(path, file_name,
                                    command='participant_cert_svg')
            if return_value == 0:
                path = Path('{0}/{1}.pdf'.format(path, file_name))
                with path.open(mode='rb') as f:
                    cm.certificate_file = File(f, name=path.name)
                    cm.save()
            else:
                has_error = True
    except Exception as e:
        has_error = True
        msg = e
    return [cm, True] 
            

def _make_certificate_certificate(path, file_name, command='participant_cert'):
    process = subprocess.Popen('timeout {0} make -C {1} {2} file_name={3}'.format(settings.TIME_OUT, path, command, file_name),
                               stderr=subprocess.PIPE, shell=True)
    err = process.communicate()[1]
    return process.returncode, err


def _clean_certificate_certificate(path, file_name):
    clean_process = subprocess.Popen('make -C {0} clean file_name={1}'.format(path, file_name),
                                     shell=True)
    clean_process.wait()

