import logging
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
import jwt

from .models import Person, Location
from .constants import DYNAMIC_FILTER_FIELDS, FIELD_LABLES

logger = logging.getLogger('api')

def _decode_permissions(request):
    """Return query permissions embedded in the JWT access token."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("queryPermissions", [])
        except jwt.PyJWTError as exc:
            logger.warning("Failed to decode access token: %s", exc)
    return []

def _apply_permission_filters(qs, perms, base):
    """Filter ``qs`` using the provided permission objects."""
    relevant = [p for p in perms if p.get("resource") == base]
    if not relevant:
        return qs.none()
    
    perm_q = Q()
    for perm in relevant:
        conds = {}
        conds.update(perm.get("view_limits") or {})
        conds.update(perm.get("filters") or {})
        
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
    applied = {}
    for rf in filters:
        if ":" in rf:
            fld, val = rf.split(":", 1)
            applied.setdefault(fld, []).append(val)
    for fld, vals in applied.items():
        qs = qs.filter(**{f"{fld}__in": vals})
    return qs

class FilterTreeView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Filter Tree Request recieved.')
        base = request.query_params.get("base", "person")
        filters = request.query_params.getlist("filters")

        perms = _decode_permissions(request)

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
        filters = request.query_params.getlist("filters")

        perms = _decode_permissions(request)

        qs = Location.objects.all() if base == "location" else Person.objects.all()
        qs = _apply_permission_filters(qs, perms, base)
        qs = _apply_user_filters(qs, filters)
        qs = qs.distinct()

        data = list(qs.values())

        return Response({"results": data})

class SearchResultsView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q", "").strip()

        perms = _decode_permissions(request)

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
