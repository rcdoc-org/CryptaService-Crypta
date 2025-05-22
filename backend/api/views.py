import json
import os
from datetime import datetime
import logging
from itertools import groupby
import pandas as pd
from django.http import JsonResponse, Http404
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

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

def changeLog(request):
    return render(request, 'changeLog.html')

def details_page(request, base, pk):
    if request.method == 'POST' and request.FILES.get('photo'):
        # handle file upload
        slug = base.lower()
        if slug in ('person', 'persons'):
            Model = Person
            ctx_base = 'person'
        elif slug in ('location', 'locations'):
            Model = Location
            ctx_base = 'location'
        else:
            raise Http404(f"Unknown detail type: {base}")
        
        obj = get_object_or_404(Model, pk=pk)
        obj.photo = request.FILES['photo']
        obj.save()
        return redirect(request.path) # reload GET so you don’t repost on refresh
    
    slug = base.lower()
    if slug in ('person', 'persons'):
        Model = Person
        ctx_base = 'person'
    elif slug in ('location', 'locations'):
        Model = Location
        ctx_base = 'location'
    else:
        raise Http404(f"Unknown detail type: {base}")
    
    obj = get_object_or_404(Model, pk=pk)
    
    # all assignments
    assignments = obj.assignment_set.select_related(
        'lkp_location_id',
        'lkp_assignmentType_id'
    ).all()
    
    if ctx_base == 'person':
        # get the person details
        person_details = obj.priest_detail_set.first() or obj.deacon_detail_set.first() or obj.lay_detail_set.first()
        if person_details:
            obj.person_details = person_details
        else:
            obj.person_details = None
        
        # primary phone
        phones = obj.person_phone_set.all()
        primary_phone = phones.first().phoneNumber if phones.exists() and phones.first().is_primary else phones.first().phoneNumber if phones.exists() else None
        obj.primary_phone = primary_phone
        
        # primary email
        emails = obj.person_email_set.all()
        primary_email = emails.first().email if emails.exists() and emails.first().is_primary else None
        obj.primary_email = primary_email

        # diocesan email
        diocesan_email = obj.person_email_set.\
            filter(lkp_emailType_id__name='diocesan')\
                .first()
        obj.diocesan_email = diocesan_email.email
    
    if ctx_base == 'location':
        location_details = obj.churchDetail_location.first() or obj.school_location.first() or obj.otherentity_detail_set.first() or obj.hospital_location.first() or obj.campusMinistry_location.first()
        if location_details:
            obj.location_details = location_details
        else:
            obj.location_details = None
    
    obj.assignments = assignments

    # Get the object details
    records, applied, filter_tree, columns, stats_info = get_filtered_data(
        base=ctx_base,
        raw_filters=[f"id:{pk}"],
        raw_stats=None
    )
    
    detail_data = records[0] if records else {}
    # render
    return render(request, 'details_page.html', {
        'base':         ctx_base,      # 'person' or 'location'
        'object':       obj,           # your ORM object, for any custom template logic
        'detail_data':  detail_data,   # the flattened dict: detail_data["First Name"], etc
        'filter_tree':  filter_tree,   # if you ever want to rebuild the sidebar
        'applied':      applied,
        'columns':      columns,       # column metadata (title, field, category)
        'stats_info':   stats_info,    # stats_info for any numeric/boolean fields
    })

def get_filtered_data(base, raw_filters, raw_stats=None):
    """
    Returns:
      - records: list of dicts (one per object) for DataFrame/grid
      - applied: dict mapping field → [values]
      - filter_tree: list of { field, display, options }
    """

    DISPLAY_TO_PATH = {
        "% Full-Time Deacons":  'statusAnimarum_church__percentFullTime_deacons',
        "% Full-Time Brothers":  'statusAnimarum_church__percentFullTime_brothers',
        "% Full-Time Sisters":  'statusAnimarum_church__percentFullTime_sisters',
        "% Full-Time Lay":  'statusAnimarum_church__percentFullTime_other',
        "% Part-Time Staff":  'statusAnimarum_church__percentPartTime_staff',
        "% Volunteers":  'statusAnimarum_church__percent_volunteers',
        "Registered Households":  'statusAnimarum_church__registeredHouseholds',
        "Max Mass Size":  'statusAnimarum_church__maxMass',
        "Seating Capacity":  'statusAnimarum_church__seatingCapacity',
        "Baptisms 1-7":  'statusAnimarum_church__baptismAge_1_7',
        "Baptisms 8-17":  'statusAnimarum_church__baptismAge_8_17',
        "Baptisms 18+":  'statusAnimarum_church__baptismAge_18',
        "Full Communion RCIA":  'statusAnimarum_church__fullCommunionRCIA',
        "First Communion":  'statusAnimarum_church__firstCommunion',
        "Confirmation":  'statusAnimarum_church__confirmation',
        "Catholic Marriages":  'statusAnimarum_church__marriage_catholic',
        "Interfaith Marriages":  'statusAnimarum_church__marriage_interfaith',
        "Deaths":  'statusAnimarum_church__deaths',
        "Children in Faith Formation":  'statusAnimarum_church__childrenInFaithFormation',
        "Kids: PreK - 5":  'statusAnimarum_church__school_prek_5',
        "Kids: 6-8":  'statusAnimarum_church__school_grade6_8',
        "Kids: 9-12":  'statusAnimarum_church__school_grade9_12',
        "Youth Ministy":  'statusAnimarum_church__youthMinistry',
        "Adult Education":  'statusAnimarum_church__adult_education',
        "Adult Sacrament Prep":  'statusAnimarum_church__adult_sacramentPrep',
        "# Paid Catechists":  'statusAnimarum_church__catechist_paid',
        "# Volunteer Catechists":  'statusAnimarum_church__catechist_vol',
        "RCIA/RCIC":  'statusAnimarum_church__rcia_rcic',
        "# Volunteers Youth":  'statusAnimarum_church__volunteersWorkingYouth',
        "% African":  'statusAnimarum_church__percent_african',
        "% African-American":  'statusAnimarum_church__percent_africanAmerican',
        "% Asian":  'statusAnimarum_church__percent_asian',
        "% Hispanic":  'statusAnimarum_church__percent_hispanic',
        "% American-Indian":  'statusAnimarum_church__percent_americanIndian',
        "% Other":  'statusAnimarum_church__percent_other',
        "Estimate Census?":  'statusAnimarum_church__is_censusEstimate',
        "# Referrals to Catholic Charities":  'statusAnimarum_church__referrals_catholicCharities',
        "HomeSchool Program?":  'statusAnimarum_church__has_homeschoolProgram',
        "Child Care Day Care?":  'statusAnimarum_church__has_chileCareDayCare',
        "Scouting Program?":  'statusAnimarum_church__has_scoutingProgram',
        "Chapel on Campus?":  'statusAnimarum_church__has_chapelOnCampus',
        "Adoration Chapel on Campus?":  'statusAnimarum_church__has_adorationChapelOnCampus',
        "Columbarium on Site?":  'statusAnimarum_church__has_columbarium',
        "Cemetery on Site?":  'statusAnimarum_church__has_cemetary',
        "School on Site?":  'statusAnimarum_church__has_schoolOnSite',
        "NonParochial School Using Facilities?":  'statusAnimarum_church__is_nonParochialSchoolUsingFacilities',
    }
    
    FIELD_CATEGORIES = {
        # PERSON ONLY
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
        
        # LOCATION ONLY
        # Basic
        "Name":            "Basic",
        "Type":            "Basic",

        # Jurisdiction
        "Vicariate":       "Location Info",
        "County":          "Location Info",

        # Address
        "Physical Addr":   "Address",

        # Contact
        "Website":         "Contact",
        "Emails":          "Contact",
        "Phones":          "Contact",

        # Church Details
        "Parish Name":     "Church Details",
        "Is Mission":      "Church Details",
        "Boundary File":   "Church Details",
        "City Served":     "Church Details",
        "Date Established":"Church Details",
        "First Dedication":"Church Details",
        "Second Dedication":"Church Details",
        "Church Notes":    "Church Details",
        
        # School Details
        "School Code":          "School Details",
        "School Type":          "School Details",
        "Grade Levels":         "School Details",
        "Affiliated Parish":    "School Details",
        "MACS School":          "School Details",
        "Priests Teaching":     "School Details",
        "Brothers Teaching":    "School Details",
        "Sisters Teaching":     "School Details",
        "Lay Staff Teaching":   "School Details",
        "Canonical Status":     "School Details",
        "Chapel on Site":       "School Details",

        # Services
        "Mass Languages":          "Services",
        "Campus Mass At Parish":   "Services",
        "Served By":               "Services",
        "Mass Schedule":           "Services",
        "Hours":                   "Services",
        "Facility Type":           "Services",
        "Diocese":                 "Services",
        "Parish Boundary":         "Services",
        "Is Other Entity":         "Services",

        # Relations
        "Missions":       "Relations",
        "Parishes":       "Relations",

        #Statistics
        "% Full-Time Deacons":          "Statistics",
        "% Full-Time Brothers":         "Statistics",
        "% Full-Time Sisters":          "Statistics",
        "% Full-Time Lay":              "Statistics",
        "% Part-Time Staff":            "Statistics",
        "% Volunteers":                 "Statistics",
        "Registered Households":        "Statistics",
        "Max Mass Size":                "Statistics",
        "Seating Capacity":             "Statistics",
        "Baptisms 1-7":                 "Statistics",
        "Baptisms 8-17":                "Statistics",
        "Baptisms 18+":                 "Statistics",
        "Full Communion RCIA":          "Statistics",
        "First Communion":              "Statistics",
        "Confirmation":                 "Statistics",
        "Catholic Marriages":           "Statistics",
        "Interfaith Marriages":         "Statistics",
        "Deaths":                       "Statistics",
        "Children in Faith Formation":  "Statistics",
        "Kids: PreK - 5":               "Statistics",
        "Kids: 6-8":                    "Statistics",
        "Kids: 9-12":                   "Statistics",
        "Youth Ministy":                "Statistics",
        "Adult Education":              "Statistics",
        "Adult Sacrament Prep":         "Statistics",
        "# Paid Catechists":            "Statistics",
        "# Volunteer Catechists":       "Statistics",
        "RCIA/RCIC":                    "Statistics",
        "# Volunteers Youth":           "Statistics",
        "% African":                    "Statistics",
        "% African-American":           "Statistics",
        "% Asian":                      "Statistics",
        "% Hispanic":                   "Statistics",
        "% American-Indian":            "Statistics",
        "% Other":                      "Statistics",
        "Estimate Census?":             "Statistics",
        "# Referrals to Catholic Charities":            "Statistics",
        "HomeSchool Program?":          "Statistics",
        "Child Care Day Care?":         "Statistics",
        "Scouting Program?":            "Statistics",
        "Chapel on Campus?":            "Statistics",
        "Adoration Chapel on Campus?":  "Statistics",
        "Columbarium on Site?":         "Statistics",
        "Cemetery on Site?":            "Statistics",
        "School on Site?":              "Statistics",
        "NonParochial School Using Facilities?":        "Statistics",
        
    }
    
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
                "school_location",
                
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

    # Apply raw_stats filters
    if raw_stats:
        # collect all numeric bounds by field
        ranges = {}
        for key, val in raw_stats.items():
            if key.endswith("_min"):
                fld = key[:-4]
                ranges.setdefault(fld, {})['min'] = val
            elif key.endswith('_max'):
                fld = key[:-4]
                ranges.setdefault(fld, {})['max'] = val
        
        # apply numeric filters
        for fld, b in ranges.items():
            real = DISPLAY_TO_PATH.get(fld)
            
            if not real:
                continue
            
            lo = b.get('min')
            hi = b.get('max')
            
            if lo is not None and hi is not None:
                qs = qs.filter(**{f"{real}__range": (lo, hi)})
            elif lo is not None:
                qs = qs.filter(**{f"{real}__gte": lo})
            elif hi is not None:
                qs = qs.filter(**{f"{real}__lte": hi})
                
        # Boolean stats
        for key, val in raw_stats.items():
            if key.endswith('_min') or key.endswith('_max'):
                continue
            
            real = DISPLAY_TO_PATH.get(key)
            if not real:
                continue
            
            qs = qs.filter(**{real: val.lower() == 'true'})

    qs = qs.distinct()

    records = []
    for obj in qs:
        if base == "person":
            rec = {
                "id":               obj.pk,   # for the DataFrame/grid
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
                            pr_det.date_priestOrdination.isoformat() 
                                if pr_det.date_priestOrdination else "",
                        "Diocesan/Religious": 
                            pr_det.diocesanReligious or "",
                        "Place of Baptism":   
                            pr_det.lkp_placeOfBaptism_id.name 
                                if pr_det.lkp_placeOfBaptism_id else "",
                        "Birth (City,State)":  
                            f"{pr_det.birth_city or ''}, {pr_det.birth_state or ''}",
                        "Priest Notes":        
                            pr_det.notes or "",
                        # …and guard any other fields the same way…
                    }
                    if (pr_det := obj.priest_detail_set.first())
                    else {}
                    ),
            }
        else:
            rec = {
                "id":               obj.pk,   # for the DataFrame/grid
                # — Basic info —
                "Name":             obj.name,
                "Type":             obj.type,

                # — Location & jurisdiction —
                "Vicariate":        obj.lkp_vicariate_id.name if obj.lkp_vicariate_id else "",
                "County":           obj.lkp_county_id.name    if obj.lkp_county_id    else "",

                # — Addresses —
                "Physical Addr":    f"{obj.lkp_physicalAddress_id.address1}, "
                                    f"{obj.lkp_physicalAddress_id.city}"
                                    if obj.lkp_physicalAddress_id else "",
                "Mailing Addr":     f"{obj.lkp_mailingAddress_id.address1}, "
                                    f"{obj.lkp_mailingAddress_id.city}"
                                    if obj.lkp_mailingAddress_id else "",

                # — Contact —
                "Website":          obj.website or "",
                "Emails":           ", ".join(e.email for e in obj.location_email_set.all()),
                "Phones":           ", ".join(p.phoneNumber for p in obj.location_phone_set.all()),

                # — Status history —
                "Status History":   "; ".join(
                                        f"{st.lkp_status_id.name}"
                                        f" ({st.date_assigned}"
                                        f"→{st.date_released or 'present'})"
                                        for st in obj.location_status_set.all()
                                    ),
                
                # — “Other Entity” flag —
                "Is Other Entity": obj.otherentity_detail_set.exists(),

                # — Assignments & relationships —
                "Assignments":      "; ".join(
                                        f"{a.lkp_assignmentType_id.title}"
                                        f"@{a.lkp_person_id.name}"
                                        f" ({a.date_assigned}"
                                        f"→{a.date_released or 'present'})"
                                        for a in obj.assignment_set.all()
                                    ),
                "Missions":         ", ".join(m.lkp_parish_id.name
                                        for m in obj.mission.all()),
                "Parishes":         ", ".join(p.lkp_mission_id.name
                                        for p in obj.parish.all()),
            }

            # — Church‐specific details (if any) —
            cd = obj.churchDetail_location.first()
            
            if cd:
                rec.update({
                    "Parish Name":       cd.parishUniqueName,
                    "Is Mission":        cd.is_mission,
                    "Boundary File":     cd.boundary.name if cd.boundary else "",
                    "City Served":       cd.cityServed or "",
                    "Date Established":  cd.date_established.isoformat() if cd.date_established else "",
                    "First Dedication":  cd.date_firstDedication.isoformat() if cd.date_firstDedication else "",
                    "Second Dedication": cd.date_secondDedication.isoformat() if cd.date_secondDedication else "",
                    "Church Notes":      cd.notes or "",
                    "Mass Languages":   "; ".join(
                                    f"{cl.lkp_language_id.name} @ {cl.massTime}"
                                    for cl in obj.church_language_set.all()
                                ),
                }),

            # — Campus ministry details (if any) —
            cm = obj.campusMinistry_location.first()
            if cm:
                rec.update({
                    "Campus Mass At Parish": cm.is_massAtParish,
                    "Served By":             cm.universityServed or "",
                    "Mass Schedule":         cm.sundayMassSchedule or "",
                    "Hours":                 cm.campusMinistryHours or "",
                })

            # — Hospital details (if any) —
            hd = obj.hospital_location.first()
            if hd:
                rec.update({
                    "Facility Type":   hd.facilityType,
                    "Diocese":         hd.diocese,
                    "Parish Boundary": hd.lkp_parishBoundary.name if hd.lkp_parishBoundary.name else "",
                })

            sc = obj.school_location.first()
            if sc:
                rec.update({
                    "School Code":      sc.schoolCode,
                    "School Type":      sc.schoolType,
                    "Grade Levels":     sc.gradeLevels,
                    "MACS School":      sc.is_MACS,
                    "Priests Teaching": sc.academicPriest,
                    "Brothers Teaching":    sc.academicBrother,
                    "Sisters Teaching": sc.academicSister,
                    "Lay Staff Teaching":   sc.academicLay,
                    "Canonical Status": sc.canonicalStatus,
                    "Chapel on Site":   sc.is_schoolChapel,
                })
            
            sa = obj.statusAnimarum_church.first()
            if sa:
                rec.update({
                    "% Full-Time Deacons":  sa.percentFullTime_deacons,
                    "% Full-Time Brothers":  sa.percentFullTime_brothers,
                    "% Full-Time Sisters":  sa.percentFullTime_sisters,
                    "% Full-Time Lay":  sa.percentFullTime_other,
                    "% Part-Time Staff":  sa.percentPartTime_staff,
                    "% Volunteers":  sa.percent_volunteers,
                    "Registered Households":  sa.registeredHouseholds,
                    "Max Mass Size":  sa.maxMass,
                    "Seating Capacity":  sa.seatingCapacity,
                    "Baptisms 1-7":  sa.baptismAge_1_7,
                    "Baptisms 8-17":  sa.baptismAge_8_17,
                    "Baptisms 18+":  sa.baptismAge_18,
                    "Full Communion RCIA":  sa.fullCommunionRCIA,
                    "First Communion":  sa.firstCommunion,
                    "Confirmation":  sa.confirmation,
                    "Catholic Marriages":  sa.marriage_catholic,
                    "Interfaith Marriages":  sa.marriage_interfaith,
                    "Deaths":  sa.deaths,
                    "Children in Faith Formation":  sa.childrenInFaithFormation,
                    "Kids: PreK - 5":  sa.school_prek_5,
                    "Kids: 6-8":  sa.school_grade6_8,
                    "Kids: 9-12":  sa.school_grade9_12,
                    "Youth Ministy":  sa.youthMinistry,
                    "Adult Education":  sa.adult_education,
                    "Adult Sacrament Prep":  sa.adult_sacramentPrep,
                    "# Paid Catechists":  sa.catechist_paid,
                    "# Volunteer Catechists":  sa.catechist_vol,
                    "RCIA/RCIC":  sa.rcia_rcic,
                    "# Volunteers Youth":  sa.volunteersWorkingYouth,
                    "% African":  sa.percent_african,
                    "% African-American":  sa.percent_africanAmerican,
                    "% Asian":  sa.percent_asian,
                    "% Hispanic":  sa.percent_hispanic,
                    "% American-Indian":  sa.percent_americanIndian,
                    "% Other":  sa.percent_other,
                    "Estimate Census?":  sa.is_censusEstimate,
                    "# Referrals to Catholic Charities":  sa.referrals_catholicCharities,
                    "HomeSchool Program?":  sa.has_homeschoolProgram,
                    "Child Care Day Care?":  sa.has_chileCareDayCare,
                    "Scouting Program?":  sa.has_scoutingProgram,
                    "Chapel on Campus?":  sa.has_chapelOnCampus,
                    "Adoration Chapel on Campus?":  sa.has_adorationChapelOnCampus,
                    "Columbarium on Site?":  sa.has_columbarium,
                    "Cemetery on Site?":  sa.has_cemetary,
                    "School on Site?":  sa.has_schoolOnSite,
                    "NonParochial School Using Facilities?":  sa.is_nonParochialSchoolUsingFacilities,
                })


        records.append(rec)

    all_fields = []
    for r in records:
        for key in r.keys():
            if key not in all_fields:
                all_fields.append(key)
    
    columns = [
        {
            "title":    key,
            "field":    key,
            "category": FIELD_CATEGORIES.get(key, "Other")
        }
        for key in all_fields
    ]
    
        # Compute stats_info on the pre-filtered qs
    stats_info = []
    for col in columns:
        if col["category"] != 'Statistics':
            continue
        
        field = col["field"]
        # Pull all the non-None values out of the records
        vals = [ rec[field] for rec in records if rec.get(field) is not None]
        
        if not vals:
            continue
        
        # Boolean Check
        if all(isinstance(v, bool) for v in vals):
            stats_info.append({
                'field': field,
                'display': col['title'],
                'type': 'boolean',
                })
        else:
            nums = [float(v) for v in vals]
            stats_info.append({
                'field': field,
                'display': col['title'],
                'type': 'number',
                'min': min(nums),
                'max': max(nums),
            })
            
    # build your filter_tree as before…
    # return also the `columns` list
    return records, applied, filter_tree, columns, stats_info

def enhanced_filter_view(request):
    """Initial page load: no filters yet."""
    # default to person-based
    records, applied, filter_tree, columns, stats_info = get_filtered_data(base="person", raw_filters=[], raw_stats=None)
    # send initial column list if you wish to prerender the grid
    return render(request, "enhanced_filter.html", {
        "filter_tree": filter_tree,
        "applied": applied,
        'stats_info': stats_info,
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
    stats_info = payload.get('stats', {})

    # reuse the exact same logic
    records, applied, filter_tree, columns, stats_info = get_filtered_data(base, raw_filters, stats_info)

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
      'stats_info': stats_info,
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

@require_POST
@csrf_exempt
def email_count_preview(request):
    
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # 1. Build the same base-QS you use in get_filtered_data()
    base    = data.get('base', 'person')
    raw_f   = data.get('filters', [])
    qs      = Location.objects.all() if base == 'location' else Person.objects.all()

    # 2. Apply each filter “field:value” as an __in
    applied = {}
    for rf in raw_f:
        if ':' not in rf:
            continue
        fld, val = rf.split(':', 1)
        applied.setdefault(fld, []).append(val)

    for fld, vals in applied.items():
        qs = qs.filter(**{f"{fld}__in": vals})
    qs = qs.distinct()

    # 3. Collect emails exactly like your get_*_list helpers do
    recipients = []
    if data.get('personalEmail'):
        if base == 'location':
            recipients += list(Location_Email.objects
                                .filter(lkp_location_id__in=qs,
                                        lkp_emailType_id__name__iexact='Personal')
                                .values_list('email', flat=True))
        else:
            recipients += list(Person_Email.objects
                                .filter(lkp_person_id__in=qs,
                                        lkp_emailType_id__name__iexact='Personal')
                                .values_list('email', flat=True))
    if data.get('parishEmail'):
        # same pattern...
        if base == 'location':
            recipients += list(Location_Email.objects
                                .filter(lkp_location_id__in=qs,
                                        lkp_emailType_id__name__iexact='Parish')
                                .values_list('email', flat=True))
        else:
            recipients += list(Person_Email.objects
                                .filter(lkp_person_id__in=qs,
                                        lkp_emailType_id__name__iexact='Parish')
                                .values_list('email', flat=True))
    if data.get('diocesanEmail'):
        if base == 'location':
            recipients += list(Location_Email.objects
                                .filter(lkp_location_id__in=qs,
                                        lkp_emailType_id__name__iexact='Diocesan')
                                .values_list('email', flat=True))
        else:
            recipients += list(Person_Email.objects
                                .filter(lkp_person_id__in=qs,
                                        lkp_emailType_id__name__iexact='Diocesan')
                                .values_list('email', flat=True))

    unique_count = len(set(recipients))
    return JsonResponse({'count': unique_count})

def search(request):
    q = request.GET.get('q', '').strip()
    persons     = Person.objects.filter(
        Q(name_first__icontains=q) |
        Q(name_last__icontains=q) |
        Q(name_middle__icontains=q)
    )
    locations   = Location.objects.filter(name__icontains=q)
    results     = list(persons) + list(locations)
    
    if len(results) == 1:
        obj = results[0]
        base = 'person' if isinstance(obj, Person) else 'location'
        return redirect('api:details_page', base=base, pk=obj.pk)
    
    return render(request, 'search_results.html', {
        'query': q,
        'persons': persons,
        'locations': locations,
    })