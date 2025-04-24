import json
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from .models import Person, Location

# Dynamic filter configuration mapping base types to model fields or joins
DYNAMIC_FILTER_FIELDS = {
    'person': [
        # Direct CharFields / choices on Person
        'personType',                # e.g. Priest / Deacon / Lay Person
        'prefix',                    # Mr. / Dr. / Reverend / etc.
        'residencyType',             # Your residencyType field
        'activeOutsideDOC',          # Active outside DOC choices
        'legalStatus',               # Legal status choices

        # Boolean
        'is_safeEnvironmentTraining',  # True / False

        # DateFields
        'date_baptism',              # Baptism date
        'date_deceased',             # Deceased date
        'date_retired',              # Retirement date

        # ForeignKey → Address (residence & mailing)
        'lkp_residence_id__city',    # Residence city
        'lkp_residence_id__state',   # Residence state (if exists)
        'lkp_mailing_id__city',      # Mailing address city
        'lkp_mailing_id__state',     # Mailing state (if exists)

        # Reverse rel’n from Assignment
        'assignment__lkp_assignmentType_id__title',   # Assignment type title
        'assignment__lkp_location_id__name',          # Location name from assignments
        'assignment__date_assigned',                  # Assignment date (if you want)

        # Reverse rel’n from Person_Status
        'person_status__lkp_status_id__name',         # Status name
        'person_status__date_assigned',               # When status assigned
    ],
    'location': [
        'lkp_physicalAddress_id__city',              # simple field on Location
        'lkp_county_id__name',            # simple field
    ],
}

# Create your views here.
def view_404(request):
    return render(request, '404.html', status=404)

def home(request):
    return render(request, 'home.html')

@csrf_exempt
def filter_results(request):
    """
    AJAX endpoint:
    - Accepts JSON payload { base: 'person'|'location', filters: ['field:value', ...] }
    - Applies filters, rebuilds dynamic filter tree, and returns HTML snippets.
    """
    # Parse JSON payload
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    base = payload.get('base')
    raw_filters = payload.get('filters', [])

    # Build base queryset
    if base == 'location':
        qs = Location.objects.all()
    else:
        qs = Person.objects.all()

    # Apply filters passed as 'field:value'
    applied = {}
    for rf in raw_filters:
        if ':' in rf:
            field, val = rf.split(':', 1)
            applied[field] = val
    if applied:
        qs = qs.filter(**applied).distinct()

    # Build dynamic filter tree based on remaining queryset
    filter_tree = []
    for path in DYNAMIC_FILTER_FIELDS.get(base, []):
        if path in applied:
            continue
        buckets = (
            qs.values(path)
              .annotate(count=Count(path))
              .order_by()
        )
        options = [
            {'value': r[path], 'label': r[path], 'count': r['count']}
            for r in buckets if r[path] is not None
        ]
        if options:
            filter_tree.append({'field': path, 'options': options})

    # Render updated filters and results
    filters_html = render_to_string(
        'partials/filter_dynamic.html',
        {'filter_tree': filter_tree, 'applied': applied},
        request=request
    )
    results_html = render_to_string(
        'partials/results_list.html',
        {'items': qs},
        request=request
    )

    return JsonResponse({'filters_html': filters_html, 'results_html': results_html})


def enhanced_filter_view(request):
    """
    Serves the initial enhanced filter demo page with an unfiltered view.
    """
    # Default to person-based view
    base = 'person'
    qs = Person.objects.all()

    # Build initial dynamic filter tree
    initial_tree = []
    for path in DYNAMIC_FILTER_FIELDS[base]:
        buckets = (
            qs.values(path)
              .annotate(count=Count(path))
              .order_by()
        )
        options = [
            {'value': r[path], 'label': r[path], 'count': r['count']}
            for r in buckets if r[path] is not None
        ]
        if options:
            initial_tree.append({'field': path, 'options': options})

    # Initial results (limit to first 50)
    items = qs[:50]
    applied = {}

    return render(request, 'enhanced_filter.html', {
        'filter_tree': initial_tree,
        'items': items,
        'applied': applied,
    })
