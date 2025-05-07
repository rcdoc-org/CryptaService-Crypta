import json
import os
from datetime import datetime
import logging
from itertools import groupby
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
    if base == "person":
        qs = qs.select_related(
                "lkp_residence_id", "lkp_mailing_id"
            ).prefetch_related(
                # built-in reverse FK sets:
                "person_email_set",
                "person_phone_set",
                "person_language_set",
                "person_facultiesgrant_set",
                "person_title_set", 
                "person_status_set",
                "person_degreecertificate_set",
                
                # detail tables:
                "deacon_detail_set",
                "lay_detail_set",
                "priest_detail_set",
                
                # assignments & vicariate:
                "assignment_set",
                "vicariate_set",
                
                # explicit related_names on person_relationship:
                "first_person",
                "second_person",
            )
    else:
        qs = qs.select_related(
                "lkp_physicalAddress_id", "lkp_mailingAddress_id",
                "lkp_vicariate_id", "lkp_county_id"
            ).prefetch_related(
                # built-in reverse FK sets:
                "location_email_set",
                "location_phone_set",
                "location_status_set",
                "church_language_set",

                # detail tables:
                "churchDetail_location",
                "campusMinistry_location",
                "hospital_location",
                "otherentity_detail_set",
                
                # assignments:
                "assignment_set",
                
                # Location Relationships
                "churchDetail_mission",
                "campusMinistry_church",
                "hospital_boundary",
                "mission",
                "parish",
                
                # baptism place
                "priest_detail_set",
                
                #schools
                "school_affiliatedParish",
                "school_parishProperty",
                
                # Statistics
                "enrollment_set",
                "octoberCount_church",
                "statusAnimarum_church",
                
            )

    records = []
    for obj in qs:
        if base == "person":
            rec = {
                # core Person fields
                "Full Name":        obj.name,
                "First Name":       obj.name_first,
                "Middle Name":      obj.name_middle,
                "Last Name":        obj.name_last,
                "Person Type":      obj.personType,
                "Prefix":           obj.prefix or "",
                "Suffix":           obj.suffix or "",
                "Birth Date":       obj.date_birth and obj.date_birth.isoformat() or "",
                "Baptism Date":     obj.date_baptism and obj.date_baptism.isoformat() or "",
                "Retirement Date":  obj.date_retired and obj.date_retired.isoformat() or "",
                "Deceased Date":    obj.date_deceased and obj.date_deceased.isoformat() or "",
                "Safe Env Trng":    obj.is_safeEnvironmentTraining,
                "Paid Employee":    obj.is_paidEmployee,

                # flattened addresses
                "Residence Addr":   obj.lkp_residence_id and obj.lkp_residence_id.address1 or "",
                "Residence City":   obj.lkp_residence_id and obj.lkp_residence_id.city or "",
                "Residence State":  obj.lkp_residence_id and obj.lkp_residence_id.state or "",
                "Residence Zip Code":   obj.lkp_residence_id and obj.lkp_residence_id.zip_code or "",
                "Residence Country":    obj.lkp_residence_id and obj.lkp_residence_id.country or "",    
                "Mailing Addr":     obj.lkp_mailing_id and obj.lkp_mailing_id.address1 or "",
                "Mailing City":     obj.lkp_mailing_id and obj.lkp_mailing_id.city or "",
                "Mailing State":    obj.lkp_mailing_id and obj.lkp_mailing_id.state or "",
                "Mailing Zip Code": obj.lkp_mailing_id and obj.lkp_mailing_id.zip_code or "",
                "Mailing Country":  obj.lkp_mailing_id and obj.lkp_mailing_id.country or "",

                # emails & phones
                "Personal Emails":  ", ".join(e.email for e in obj.person_email_set
                                                .filter(lkp_emailType_id__name__iexact="Personal")),
                "Parish Emails":    ", ".join(e.email for e in obj.person_email_set
                                                .filter(lkp_emailType_id__name__iexact="Parish")),
                "Diocesan Emails":  ", ".join(e.email for e in obj.person_email_set
                                                .filter(lkp_emailType_id__name__iexact="Diocesan")),

                "Cell Phones":      ", ".join(p.phoneNumber for p in obj.person_phone_set
                                                .filter(lkp_phoneType_id__name__iexact="Cell")),
                "Home Phones":      ", ".join(p.phoneNumber for p in obj.person_phone_set
                                                .filter(lkp_phoneType_id__name__iexact="Home")),

                # languages
                "Languages":        ", ".join(
                                    f"{pl.lkp_language_id.name} ({pl.lkp_languageProficiency_id.name})"
                                    for pl in obj.person_language_set.all()
                                ),

                # degrees & certificates
                "Degrees":          "; ".join(
                                    f"{dc.lkp_degreeCertificate_id.institute}"
                                    f" (acquired {dc.date_acquired}, expires {dc.date_expiration})"
                                    for dc in obj.person_degreecertificate_set.all()
                                ),

                # faculties grants
                "Faculties Grants": "; ".join(
                                    f"{fg.lkp_faultiesGrantType_id.name}"
                                    f" (granted {fg.date_granted})"
                                    for fg in obj.person_facultiesgrant_set.all()
                                    ),

                # status history
                "Status History":   "; ".join(
                                    f"{st.lkp_status_id.name}"
                                    f" ({st.date_assigned} → {st.date_released or 'present'})"
                                    for st in obj.person_status_set.all()
                                ),

                # titles
                "Titles":           "; ".join(
                                    f"{t.lkp_title_id.name}"
                                    f" ({t.date_assigned} → {t.date_expiration or 'present'})"
                                    for t in obj.person_title_set.all()
                                ),

                # assignments
                "Assignments":      "; ".join(
                                    f"{a.lkp_assignmentType_id.title}@{a.lkp_location_id.name}"
                                    f" (term {a.term}, {a.date_assigned}→{a.date_released or 'present'})"
                                    for a in obj.assignment_set.all()
                                ),

                # relationships (both directions)
                "Relationships":    "; ".join(
                                    f"{rel.lkp_relationshipType_id.name}: "
                                    f"{(rel.lkp_secondPerson_id if rel in obj.first_person.all() else rel.lkp_firstPerson_id).name}"
                                    for rel in list(obj.first_person.all()) + list(obj.second_person.all())
                                ),

                # detail flags
                "Is Priest?":       obj.priest_detail_set.exists(),
                "Is Deacon?":       obj.deacon_detail_set.exists(),
                "Is Lay?":          obj.lay_detail_set.exists(),

                # priest‐specific fields (if any)
                **(
                    {
                        # take the first detail record
                        "Priest Ordination": 
                            pd.date_priestOrdination.isoformat() 
                                if pd.date_priestOrdination else "",
                        "Diocesan/Religious": 
                            pd.diocesanReligious or "",
                        "Place of Baptism":   
                            pd.lkp_placeOfBaptism_id.name 
                                if pd.lkp_placeOfBaptism_id else "",
                        "Birth (City,State)":  
                            f"{pd.birth_city or ''}, {pd.birth_state or ''}",
                        "Priest Notes":        
                            pd.notes or "",
                        # …and guard any other fields the same way…
                    }
                    if (pd := obj.priest_detail_set.first())
                    else {}
                    ),
            }

            category = {
                # — Basic info —
                "Full Name":          "Basic",
                "First Name":         "Basic",
                "Middle Name":        "Basic",
                "Last Name":          "Basic",
                "Person Type":        "Basic",
                "Prefix":             "Basic",
                "Suffix":             "Basic",

                # — Dates —
                "Birth Date":         "Dates",
                "Baptism Date":       "Dates",
                "Retirement Date":    "Dates",
                "Deceased Date":      "Dates",

                # — Flags —
                "Safe Env Trng":      "Flags",
                "Paid Employee":      "Flags",
                "Is Priest?":         "Flags",
                "Is Deacon?":         "Flags",
                "Is Lay?":            "Flags",

                # — Addresses —
                "Residence Addr":     "Residence Info",
                "Residence City":     "Residence Info",
                "Residence State":     "Residence Info",
                "Residence Zip Code":     "Residence Info",
                "Residence Country":     "Residence Info",
                "Mailing Addr":       "Mailing Info",
                "Mailing City":       "Mailing Info",
                "Mailing State":       "Mailing Info",
                "Mailing Zip Code":       "Mailing Info",
                "Mailing Country":       "Mailing Info",

                # — Contact —
                "Personal Emails":    "Contact",
                "Parish Emails":      "Contact",
                "Diocesan Emails":    "Contact",
                "Cell Phones":        "Contact",
                "Home Phones":        "Contact",

                # — Skills & Education —
                "Languages":          "Skills",
                "Degrees":            "Skills",
                "Faculties Grants":   "Skills",

                # — History —
                "Status History":     "History",
                "Titles":             "History",
                "Assignments":        "History",
                "Relationships":      "History",

                # — Priest Details —
                "Priest Ordination":      "Priest Details",
                "Diocesan/Religious":      "Priest Details",
                "Place of Baptism":        "Priest Details",
                "Birth (City,State)":      "Priest Details",
                "Priest Notes":            "Priest Details",
            }
        else:
            rec = {
                "Name":            obj.name,
                "Type":            obj.type,
                "Physical City":   obj.lkp_physicalAddress_id.city if obj.lkp_physicalAddress_id else "",
                "Mailing City":    obj.lkp_mailingAddress_id.city if obj.lkp_mailingAddress_id else "",
                "Website":         obj.website or "",
                "Emails":          ", ".join(e.email for e in obj.location_email_set.all()),
                "Phones":          ", ".join(p.phoneNumber for p in obj.location_phone_set.all()),
                # …
            }
            category = {
                "Name":"Basic",
                "Type":"Basic",
                "Physical City":"Address",
                "Mailing City":"Address",
                "Website":"Contact",
                "Emails":"Contact",
                "Phones":"Contact",
            }

        # build the column-metadata once
        if not records:
            columns = [
                {"title": title, "field": title, "category": category[title]}
                for title in rec.keys()
            ]
        records.append(rec)

    # build your filter_tree as before…
    # return also the `columns` list
    return records, applied, filter_tree, columns

def enhanced_filter_view(request):
    """Initial page load: no filters yet."""
    # default to person-based
    records, applied, filter_tree, columns = get_filtered_data(base="person", raw_filters=[])
    # send initial column list if you wish to prerender the grid
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
    records, applied, filter_tree, columns = get_filtered_data(base, raw_filters)

    # re-render your sidebar
    filters_html = render_to_string(
        "partials/filter_dynamic.html",
        {"filter_tree": filter_tree, "applied": applied},
        request=request
    )

    # prepare grid payload
    df      = pd.DataFrame(records)

    return JsonResponse({
      "filters_html": filters_html,
      "grid": {
          "data":   records,
          "columns": columns,
        },
    })

@csrf_exempt
def upload_temp(request):
    if request.method == 'POST' and request.FILES.get('attachment'):
        f = request.FILES['attachment']
        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f'{f.name}'
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
        
        logger.exception("send_email POST data: %r", dict(request.POST))
        
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

        return redirect('api:enhanced_filter')

    # if GET, just render the enhanced filter page
    return render(request, 'api:enhanced_filter')

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
