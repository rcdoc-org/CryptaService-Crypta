import logging
import json
from django.db.models import Count, Q, Model
from django.forms.models import model_to_dict
from django.db.models.fields.files import FileField, ImageField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, viewsets
from .serializers import PersonSerializer, LocationSerializer
from .utilities import get_query_permissions

from .models import Person, Location
from .constants import DYNAMIC_FILTER_FIELDS, FIELD_LABLES, RELETIVE_RELATIONS

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
        )

def _serialize_instance(obj):
    """Return ``obj`` as a dict including first-level related data."""
    # data = model_to_dict(obj, fields=[f.name for f in obj._meta.fields])

    # for rel in obj._meta.get_fields():
    #     if rel.one_to_many and rel.auto_created:
    #         mgr = getattr(obj, rel.get_accessor_name())
    #         data[rel.get_accessor_name()] = [
    #             model_to_dict(child, fields=[f.name for f in child._meta.fields])
    #             for child in mgr.all()
    #         ]
    #     elif rel.many_to_many and not rel.auto_created:
    #         mgr = getattr(obj, rel.name)
    #         data[rel.name] = [
    #             model_to_dict(child, fields=[f.name for f in child._meta.fields])
    #             for child in mgr.all()
    #         ]
    #     elif rel.many_to_many and rel.auto_created:
    #         mgr = getattr(obj, rel.get_accessor_name())
    #         data[rel.get_accessor_name()] = [
    #             model_to_dict(child, fields=[f.name for f in child._meta.fields])
    #             for child in mgr.all()
    #         ]
    #     elif (rel.many_to_one or rel.one_to_one) and rel.concrete:
    #         val = getattr(obj, rel.name)
    #         if val is not None:
    #             data[rel.name] = model_to_dict(
    #                 val, fields=[f.name for f in val._meta.fields]
    #             )

    # return data
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
                    "display": FIELD_LABLES.get(path, path.replace("__", " ").title()),
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

        data = _get_full_results(base, perms, filters)

        return Response({"results": data})

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