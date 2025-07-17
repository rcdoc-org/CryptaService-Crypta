import logging
import json
from datetime import date
from django.db.models import Count, Q, Model
from django.forms.models import model_to_dict
from django.db.models.fields.files import FileField, ImageField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, viewsets
from .serializers import PersonSerializer, LocationSerializer
from .utilities import get_query_permissions

from .models import Person, Location
from .constants import (
    DYNAMIC_FILTER_FIELDS, FIELD_LABELS, RELETIVE_RELATIONS, DISPLAY_TO_PATH,
    FIELD_CATEGORIES,
)

logger = logging.getLogger('api')

def _get_permissions(request):
    """Return query permissions passed via Gateway."""
    return get_query_permissions(request)

def _apply_permission_filters(qs, perms, base):
    """Filter ``qs`` using the provided permission objects."""
    logger.debug('Applying permission filters now.')
    relevant = [
        p
        for p in perms
        if p.get('resource') == base
        or RELETIVE_RELATIONS.get(p.get('resource')) == base
    ]
    if not relevant:
        return qs.none()
        # return qs

    logger.debug('Relevant: %s', relevant)
    perm_q = Q()
    for perm in relevant:
        conds = perm.get('filters') or {}

        sub = Q()
        for fld, val in conds.items():
            if isinstance(val, list):
                sub &= Q(**{f"{fld}__in": val})
            else:
                sub &= Q(**{fld: val})
        if not conds:
            sub &= Q()
        perm_q |= sub

    return qs.filter(perm_q)

def _apply_user_filters(qs, filters):
    logger.debug('Applying user filters.')
    applied = {}
    for rf in filters:
        if ":" in rf:
            fld, val = rf.split(":", 1)
            applied.setdefault(fld, []).append(val)
    for fld, vals in applied.items():
        qs = qs.filter(**{f"{fld}__in": vals})
    return qs

def _prefetch_for_base(qs, base):
    """Add select_related/prefetch_related for ``base`` queryset."""
    if base == "person":
        return qs.select_related(
            "lkp_residence_id",
            "lkp_mailing_id",
        ).prefetch_related(
            "person_email_set",
            "person_phone_set",
            "person_language_set",
            "person_facultiesgrant_set",
            "person_degreecertificate_set",
            "person_status_set",
            "person_title_set",
            "assignment_set",
            "first_person",
            "second_person",
            "priest_detail_set",
            "deacon_detail_set",
            "lay_detail_set",
            "first_person",
            "second_person",
        )
    else:
        return qs.select_related(
            "lkp_physicalAddress_id",
            "lkp_mailingAddress_id",
            "lkp_vicariate_id",
            "lkp_county_id",
        ).prefetch_related(
            "location_email_set",
            "location_phone_set",
            "location_status_set",
            "church_language_set",
            "social_outreach_program",
            "assignment_set",
            "churchDetail_location",
            "campusMinistry_location",
            "hospital_location",
            "otherentity_detail_set",
            "school_location",
            "churchDetail_mission",
            "campusMinistry_church",
            "hospital_boundary",
            "mission",
            "parish",
            "priest_detail_set",
            "school_parishProperty",
            "enrollment_set",
            "octoberCount_church",
            "offertory_church",
            "statusAnimarum_church",
            "ethnicity_church",
        )

def _serialize_instance(obj):
    """Return ``obj`` as a dict including first-level related data."""
    data = {}

    # Handle fields, skipping file/image fields with no file
    for f in obj._meta.fields:
        val = getattr(obj, f.name)
        if isinstance(f, (FileField, ImageField)):
            if not val:
                continue  # skip fields with no file
            data[f.name] = val.url if val else None
        else:
            data[f.name] = val

    # Handle relations
    for rel in obj._meta.get_fields():
        if rel.one_to_many and rel.auto_created:
            mgr = getattr(obj, rel.get_accessor_name())
            data[rel.get_accessor_name()] = [
                # model_to_dict(child, fields=[f.name for f in child._meta.fields])
                _safe_model_to_dict(child)
                for child in mgr.all()
            ]
        elif rel.many_to_many and not rel.auto_created:
            mgr = getattr(obj, rel.name)
            data[rel.name] = [
                # model_to_dict(child, fields=[f.name for f in child._meta.fields])
                _safe_model_to_dict(child)
                for child in mgr.all()
            ]
        elif rel.many_to_many and rel.auto_created:
            mgr = getattr(obj, rel.get_accessor_name())
            data[rel.get_accessor_name()] = [
                # model_to_dict(child, fields=[f.name for f in child._meta.fields])
                _safe_model_to_dict(child)
                for child in mgr.all()
            ]
        elif (rel.many_to_one or rel.one_to_one) and rel.concrete:
            val = getattr(obj, rel.name)
            if val is not None:
                # data[rel.name] = model_to_dict(
                #     val, fields=[f.name for f in val._meta.fields]
                # )
                data[rel.name] = _safe_model_to_dict(val)

    return data

def _safe_model_to_dict(obj):
    data = {}
    for f in obj._meta.fields:
        val = getattr(obj, f.name)
        if isinstance(f, (FileField, ImageField)):
            if not val:
                continue
            data[f.name] = val.url if hasattr(val, "url") else None
        elif isinstance(val, Model):
            data[f.name] = val.pk
        else:
            data[f.name] = val
    return data

def _get_full_results(base, perms, filters):
    qs = Location.objects.all() if base == "location" else Person.objects.all()
    qs = _apply_permission_filters(qs, perms, base)
    qs = _apply_user_filters(qs, filters)
    qs = qs.distinct()
    qs = _prefetch_for_base(qs, base)

    return [_serialize_instance(obj) for obj in qs]

def _get_filters(request):
    
    raw = request.query_params.get('filters')
    if raw is not None:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                out = []
                for key, value in data.items():
                    if isinstance(value, list):
                        out.extend(f"{key}:{val}" for val in value)
                    else:
                        out.append(f"{key}:{value}")
                return out
            return [str(data)]
        except json.JSONDecodeError:
            return [raw]
    return (
        request.query_params.getlist('filters')
        or request.query_params.getlist('filters[]')
    )

def _get_grid_results(base, perms, filters):
    """Return simplified records + columns for the Database grid."""
    qs = Location.objects.all() if base == "location" else Person.objects.all()
    qs = _apply_permission_filters(qs, perms, base)
    qs = _apply_user_filters(qs, filters)
    qs = qs.distinct()
    qs = _prefetch_for_base(qs, base)

    today = date.today()
    
    records = []
    if base == "person":
        for obj in qs:
            records.append({
                "id":               obj.pk,
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
                
                "Ecclesiastical Offices":       ", ".join(eo.lkp_title_id.name for oe in obj.person_title_set
                                                          .filter(lkp_title_id__is_ecclesiastical__iexact="True")),

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
                                    for a in obj.assignment_set
                                                .filter(date_assigned__lte=today,)
                                                .filter(
                                                    Q(date_released__isnull=True) |
                                                    Q(date_released__gte=today)
                                                )
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
            })
    else:
        for obj in qs:
            rec = {
                "id":               obj.pk,
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
                    "Site Plan":        cd.pastoralPlan.name if cd.pastoralPlan else "",
                    "DOC Parish":        cd.is_doc,
                    "Tax ID":           cd.tax_id or "",
                    "Geo ID":           cd.geo_id or "",
                    "Parish ID":        cd.parish_id or "",
                    "Church Type":      cd.type or "",
                    "Seating Capacity": cd.seatingCapacity or "",
                    "Has Home School Program": cd.has_homeschoolProgram,
                    "Has Child Card Day Care": cd.has_childCareDayCare,
                    "Has Scouting Program": cd.has_scoutingProgram,
                    "Has Chapel on Campus": cd.has_chapelOnCampus,
                    "Has Adoration Chapel on Campus": cd.has_adorationChapelOnCampus,
                    "Has Columbarium": cd.has_columbarium,
                    "Has Cemetary": cd.has_cemetary,
                    "Has School on Site": cd.has_schoolOnSite,
                    "Is Non-Parochial School Using Facilities": cd.is_nonParochialSchoolUsingFacilities,
                    "Office Contact": cd.temp_officeContact,
                    "Office Contact Email": cd.temp_officeContactEmail,
                    
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
                
            offertory_qs = obj.offertory_church.order_by('-year')
            offertory = offertory_qs.first()
            if offertory:
                rec.update({
                    'Offertory': offertory.income,
                })
            
            octMass_qs = obj.octoberCount_church.order_by('-year')
            octMass = octMass_qs.first()
            if octMass:
                total = octMass.week1 + octMass.week2 + octMass.week3 + octMass.week4
                rec.update({
                'October Mass Count': total,
                    
                })
            
            """ Found an issue where this was pulling the oldest data and not the newest. """
            # sa = obj.statusAnimarum_church.first()
            sa_qs = obj.statusAnimarum_church.order_by('-year')
            sa = sa_qs.first()
            if sa:
                rec.update({
                    "# Deacons":  sa.fullTime_deacons,
                    "# Brothers":  sa.fullTime_brothers,
                    "# Sisters":  sa.fullTime_sisters,
                    "# Lay":  sa.fullTime_other,
                    "# Staff":  sa.partTime_staff,
                    "Volunteers":  sa.volunteers,
                    "Max Mass Size":  sa.maxMass,
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
                    "# Referrals to Catholic Charities":  sa.referrals_catholicCharities,
                })
                rec["Social Outreach Programs"] = ", ".join(
                    sop.name for sop in obj.social_outreach_program.all()
                )
            
            records.append(rec)

    columns = []
    if records:
        for key in records[0].keys():
            columns.append({"title": key, "field": key})

    return records, columns

class FilterTreeView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Filter Tree Request recieved.')
        base = request.query_params.get("base", "person")
        # filters = request.query_params.getlist("filters")
        filters = _get_filters(request)
        

        perms = _get_permissions(request)
        logger.debug('Permission: %s', perms)

        qs = Location.objects.all() if base == "location" else Person.objects.all()
        qs = _apply_permission_filters(qs, perms, base)
        qs = _apply_user_filters(qs, filters)

        filter_tree = []
        for path in DYNAMIC_FILTER_FIELDS.get(base, []):
            buckets = qs.values(path).annotate(count=Count(path)).order_by()
            opts = []
            for r in buckets:
                val = r[path]
                if val is None:
                    continue
                opts.append({"value": val, "label": val, "count": r["count"]})
            if opts:
                filter_tree.append({
                    "field": path,
                    "display": FIELD_LABELS.get(path, path.replace("__", " ").title()),
                    "options": opts,
                })

        return Response({"filter_tree": filter_tree})


class FilterResultsView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        base = request.query_params.get("base", "person")
        # filters = request.query_params.getlist("filters")
        filters = _get_filters(request)

        perms = _get_permissions(request)

        records, columns = _get_grid_results(base, perms, filters)

        return Response({"grid": {"data": records, "columns": columns}})

class SearchResultsView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q", "").strip()

        perms = _get_permissions(request)

        person_qs = Person.objects.filter(
            Q(name_first__icontains=query)
            | Q(name_last__icontains=query)
            | Q(name_middle__icontains=query)
        )
        person_qs = _apply_permission_filters(person_qs, perms, "person")

        location_qs = Location.objects.filter(name__icontains=query)
        location_qs = _apply_permission_filters(location_qs, perms, "location")

        results = {
            "persons": list(person_qs.values("id", "name_first", "name_last")),
            "locations": list(location_qs.values("id", "name")),
        }

        return Response({"results": results})

class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet providing read-only access to ``Person`` objects."""

    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated]


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet providing read-only access to ``Location`` objects."""

    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]