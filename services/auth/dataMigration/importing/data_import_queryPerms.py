import os
import sys
import pandas as pd
import django
from django.db import transaction

# Django setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth.settings')
django.setup()

from api.models import (
    CryptaGroup, QueryPermission
)

# Group hierarchy logic
GROUP_PRIORITY = ["Group 1", "Group 2", "Group 3", "Group 4"]
GROUP_HIERARCHY = {
    "Group 1": ["Group 1"],
    "Group 2": ["Group 1", "Group 2"],
    "Group 3": ["Group 1", "Group 2", "Group 3"],
    "Group 4": ["Group 1", "Group 2", "Group 3", "Group 4"]
}

RESOURCE_MAP = {
    "priest_detail": "PRIESTS",
    "church_detail": "CHURCH"
}

FILE = "/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/services/auth/dataMigration/raw/SQLSchema_PriestNotes.xlsx"

def load_data(file_path):
    xls = pd.ExcelFile(file_path)
    df_priests = xls.parse("Priests")
    df_church = xls.parse("Church")
    df_priests["resource_type"] = "priest_detail"
    df_church["resource_type"] = "church_detail"
    return pd.concat([df_priests, df_church], ignore_index=True)

def get_group_instances():
    groups = {}
    # Only activate Group 1 for now.
    for name in GROUP_PRIORITY:
        if name == 'Group 1':
            group, _ = CryptaGroup.objects.update_or_create(
                name=name,
                defaults={"description": f"Access level for {name}"}
            )
            groups[name] = group
        else:
            group, _ = CryptaGroup.objects.update_or_create(
                name=name,
                defaults={
                    "description": f"Access level for {name}",
                    'is_enabled': False,
                }
            )
            groups[name] = group
    return groups

def get_permission_payload(row, group_obj, resource_type):
    try:
        group_name = CryptaGroup.objects.get(name=group_obj)
    except CryptaGroup.DoesNotExist:
        raise CryptaGroup.DoesNotExist
    return QueryPermission(
        group=group_name,
        resource_type=resource_type,
        access_type="read",
        view_limits={"fields": [row["ColumnName/Relationship"]]},
        filter_conditions={}
    )

def main():
    df = load_data(FILE)
    df = df.dropna(subset=["ColumnName/Relationship", "resource_type"])

    groups = get_group_instances()

    with transaction.atomic():
        for _, row in df.iterrows():
            for group_name in reversed(GROUP_PRIORITY):
                if pd.notna(row.get(group_name)):
                    allowed_groups = GROUP_HIERARCHY[group_name]
                    for g in allowed_groups:
                        perm = get_permission_payload(row, groups[g], row["resource_type"])
                        # Avoid duplicate permission creation
                        QueryPermission.objects.update_or_create(
                            group=perm.group,
                            resource_type=perm.resource_type,
                            access_type=perm.access_type,
                            view_limits=perm.view_limits,
                            defaults={"filter_conditions": perm.filter_conditions}
                        )
                    break  # Only apply highest priority access group

if __name__ == "__main__":
    main()
