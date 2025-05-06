import json
import os
from datetime import datetime
import logging
import pandas as pd
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Person, Location,
    Person_Email, Location_Email,
    EmailType,
)
from .constants import DYNAMIC_FILTER_FIELDS, FIELD_LABLES
from .utilities.emailingSys import message_creator, send_mail

logger = logging.getLogger(__name__)

# Create your views here.
def view_404(request):
    return render(request, '404.html', status=404)

def home(request):
    return render(request, 'home.html')

def get_filtered_data(base, raw_filters):
    """
    Returns:
      - records: list of dicts (one per object) for DataFrame/grid
      - applied: dict mapping field → [values]
      - filter_tree: list of { field, display, options }
    """
    # 1) Base queryset
    qs = Location.objects.all() if base == "location" else Person.objects.all()

    # 2) Normalize raw_filters into applied dict of lists
    applied = {}
    for rf in raw_filters:
        if ":" in rf:
            field, val = rf.split(":", 1)
            applied.setdefault(field, []).append(val)

    # 3) Apply each as __in filter
    for field, vals in applied.items():
        qs = qs.filter(**{f"{field}__in": vals})
    qs = qs.distinct()

    # 4) Build Dynamic Filter Tree exactly as before
    filter_tree = []
    for path in DYNAMIC_FILTER_FIELDS.get(base, []):
        buckets = (
            qs.values(path)
              .annotate(count=Count(path))
              .order_by()
        )
        opts = [
            {"value": r[path], "label": r[path], "count": r["count"]}
            for r in buckets if r[path] is not None
        ]
        if opts:
            filter_tree.append({
                "field":   path,
                "display": FIELD_LABLES.get(path, path.replace("__"," ").title()),
                "options": opts
            })

    # 5) Records for your grid/DataFrame
    field_names = [field.name for field in qs.model._meta.fields]
    records = list(qs.values(*field_names))  # example
    return records, applied, filter_tree

def enhanced_filter_view(request):
    """Initial page load: no filters yet."""
    # default to person-based
    records, applied, filter_tree = get_filtered_data(base="person", raw_filters=[])
    # send initial column list if you wish to prerender the grid
    columns = [{"title": col, "field": col} for col in (pd.DataFrame(records).columns)]
    return render(request, "enhanced_filter.html", {
        "filter_tree": filter_tree,
        "applied": applied,
        # optionally pass these so you can do `var initialGrid = {{ grid|safe }}`
        "initial_grid": {
          "data":    records,
          "columns": columns,
        },
    })
    
@csrf_exempt
def filter_results(request):
    """AJAX: receive { base, filters } → JSON { filters_html, grid }."""
    try:
        payload = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    base       = payload.get("base", "person")
    raw_filters= payload.get("filters", [])

    # reuse the exact same logic
    records, applied, filter_tree = get_filtered_data(base, raw_filters)

    # re-render your sidebar
    filters_html = render_to_string(
        "partials/filter_dynamic.html",
        {"filter_tree": filter_tree, "applied": applied},
        request=request
    )

    # prepare grid payload
    df      = pd.DataFrame(records)
    grid    = {
      "data":    records,
      "columns": [{"title": c, "field": c} for c in df.columns],
    }

    return JsonResponse({
      "filters_html": filters_html,
      "grid":         grid,
    })

@csrf_exempt
def upload_temp(request):
    if request.method == 'POST' and request.FILES.get('attachment'):
        f = request.FILES['attachment']
        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f'{ts}_{f.name}'
        tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        save_path = os.path.join(tmp_dir, filename)
        with open(save_path, 'wb') as dest:
            for chunk in f.chunks():
                dest.write(chunk)

        return JsonResponse({
            'filename': filename,
            'url': settings.MEDIA_URL + f'tmp/{filename}'
        })
    return JsonResponse({'error': 'No file provided.'}, status=400)

def send_email(request):
    if request.method == 'POST':
        # build the true recipients lists
        personal = get_personal_list(request)
        parish = get_parish_list(request)
        diocesan = get_diocesan_list(request)
        
        # 1. Gather checkboxes
        recipients = []
        if request.POST.get('personalEmail'): recipients += personal
        if request.POST.get('parishEmail'): recipients += parish
        if request.POST.get('diocesanEmail'): recipients += diocesan

        # 2. Always send to self for testing/demo and embed real recipients into body
        sender = settings.EMAIL_HOST_USER
        to_list = [sender]

        subject = request.POST['subject']
        body = request.POST['body']
        # prefix the listed recipients into the email body
        body = f"Intended Recipients: {', '.join(recipients)}\n\n{body}"

        # 3. Pull in the previously-saved temp file path
        attachment_url = request.POST.get('temp_attachment_path') # e.g. "/media/tmp/20250506123000_report.pdf
        if attachment_url:
            attachment_path = os.path.join(
                settings.BASE_DIR,
                attachment_url.lstrip('/')
                )
        else:
            attachment_path = None

        # 4. Build the emailMessage
        try:
            msg = message_creator(
                sender=sender,
                recipients=to_list,
                subject=subject,
                body=body,
                attachment_path=attachment_path
            )
        except Exception as e:
            logger.exception(
                "message_creator failed. "
                "sender=%r recipients=%r subject=%r body=%r attachment_path=%r",
                sender, to_list, subject, body, attachment_path
            )
            return JsonResponse({
                'error': 'Could not build email message. Check server log for details.'
            }, status=500)
            

        # 5. Send via SMTP
        send_mail(msg,
                  smptp_user=settings.EMAIL_HOST_USER,
                  smtp_pass=settings.EMAIL_HOST_PASSWORD)

        # 6. Clean up temp file
        try:
            os.remove(attachment_path)
        except OSError:
            pass

        return redirect('enhanced_filter.html')

    # if GET, just render the enhanced filter page
    return render(request, 'enhanced_filter.html')

def get_filtered_items(request):
    """Return a QuerySet of either Person or Location objects based on
    the 'base' parameter (person/location) and whatever filters you pass in.

    Args:
        request (any): HTTP request from the client
        
    Returns:
        qs (BaseManager): The filtered group of persons/locations.
    """
    base = request.POST.get('base') or request.GET.get('base', 'person')
    if base == 'location':
        qs = Location.objects.all()
    else:
        qs = Person.objects.all()

    # apply dynamic filters
    for f in request.POST.getlist('filters'):
        if ':' not in f:
            continue
        field, value = f.split(':', 1)
        qs = qs.filter(**{field: value})

    return qs

def _get_email_list(request, email_type_name):
    items = get_filtered_items(request)

    base = request.POST.get('base', 'person')
    if base == 'location':
        qs = Location_Email.objects.filter(
            lkp_location_id__in=items,
            lkp_emailType_id__name__iexact=email_type_name,
        )
    else:
        qs = Person_Email.objects.filter(
            lkp_person_id__in=items,
            lkp_emailType_id__name__iexact=email_type_name,
        )

    return list(qs.values_list('email', flat=True))

def get_personal_list(request):
    """Return a Python list of personal_email from whichever model is active.

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    return _get_email_list(request, 'Personal')

def get_parish_list(request):
    """Return a Python list of parish_email from whichever model is active.

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    return _get_email_list(request, 'Parish')

def get_diocesan_list(request):
    """Return a Python list of diocesan_email from whichever model is active.

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    return _get_email_list(request, 'Diocesan')
