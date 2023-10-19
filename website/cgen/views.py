from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages

from cgen import generator, verification

from cgen.models import Certificate, Participant, Event
import csv


def events(request):
    events = Event.objects.filter(is_published=True)
    context = {'events': events}
    return render(request, 'events.html', context)

# Create your views here.
def certificate_download(request, certificate_id):
    context= {}
    certificate = get_object_or_404(Certificate, id=certificate_id)
    context['certificate'] = certificate
    ci = RequestContext(request)
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        cm, s = generator.get_certificate(certificate_id, email)
        if not s:
            context["notregistered"] = 1
            return render(request, 'download.html', context)
        if s:
            response = HttpResponse(cm.certificate_file, content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'
            return response 
    return render(request, 'download.html', context)


def verify(request, key=None):
    context = {}
    if key is not None:
        details = verification.verify(key)
        context['details'] = details
        context['has_details'] = True
        return render(request, 'verification.html', context)
    elif request.method == 'POST':
        key = request.POST.get('key').strip()
        details = verification.verify(key)
        context['has_details'] = True
        context['details'] = details
        return render(request, 'verification.html', context)
    context['has_details'] = False
    return render(request, 'verification.html', {})

def upload_csv_participants(request, certificate_id):
    certificate = get_object_or_404(Certificate, pk=certificate_id)
    context = {'certificate': certificate}

    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.warning(request, "Please upload a CSV file.")
            return render(request, 'upload.html', context)
        csv_file = request.FILES['csv_file']
        is_csv_file, dialect = is_csv(csv_file)
        if not is_csv_file:
            messages.warning(request, "The file uploaded is not a CSV file.")
            return render(request, 'upload.html', context)
        required_fields = ['name', 'email']
        try:
            reader = csv.DictReader(
                csv_file.read().decode('utf-8').splitlines(),
                dialect=dialect)
        except TypeError:
            messages.warning(request, "Bad CSV file")
            return render(request, 'upload.html', context)
        stripped_fieldnames = [
            field.strip().lower() for field in reader.fieldnames]
        for field in required_fields:
            if field not in stripped_fieldnames:
                msg = "The CSV file does not contain the required headers"
                messages.warning(request, msg)
                return render(request, 'upload.html', context)
        reader.fieldnames = stripped_fieldnames
        dict_keys = list(stripped_fieldnames)
        dict_keys.remove('email')
        _read_user_csv(request, reader, dict_keys, certificate)
        context['message'] = 'Uploaded Successfully'
    return render(request, 'upload.html', context)


def _read_user_csv(request, reader, keys, certificate):
    counter = 0
    for row in reader:
        counter += 1
        email = row['email'].strip()
        if not email:
            messages.info(request, "{0} -- Missing Values".format(counter))
            continue
        d = {}
        for k in keys:
            d[k] = row[k]
        _add_to_participant(email, d, certificate)
    if counter == 0:
        messages.warning(request, "No rows in the CSV file")


def _add_to_participant(email, details, certificate):
    try:
        p, created = Participant.objects.get_or_create(email=email,
                                                       certificate=certificate)
        p.details = f"{details}"
        p.save()
    except Exception as e:
        print(e)

def is_csv(document):
    ''' Check if document is csv with ',' as the delimiter'''
    try:
        try:
            content = document.read(1024).decode('utf-8')
        except AttributeError:
            document.seek(0)
            content = document.read(1024)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(content, delimiters=',')
        document.seek(0)
    except (csv.Error, UnicodeDecodeError):
        return False, None
    return True, dialect 
