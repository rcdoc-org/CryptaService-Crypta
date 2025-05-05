import json
import os
from datetime import datetime
import pandas as pd
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt

from .models import Person, Location
from .constants import DYNAMIC_FILTER_FIELDS, FIELD_LABLES

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