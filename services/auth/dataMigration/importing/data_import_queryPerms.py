import os
import sys
import pandas as pd
import django
from collections import defaultdict
from django.db import transaction

# Django setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth.settings')
django.setup()

from api.models import CryptaGroup, QueryPermission

# File location
FILE = "/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/services/auth/dataMigration/raw/SQLSchema_PriestNotes.xlsx"

# Group hierarchy logic
GROUP_PRIORITY = ["Group 1", "Group 2", "Group 3", "Group 4"]
GROUP_DESCRIPTIONS = {
    'Group 1': 'Access level for Chancery.',
    'Group 2': 'Access level for Chancery, Department Heads, & Designees.',
    'Group 3': 'Access level for Chancery, Department Heads, Clergy, & Designees.',
    'Group 4': 'Access level for all employees and volunteers.',
}
GROUP_HIERARCHY = {
    "Group 1": ["Group 1"],
    "Group 2": ["Group 1", "Group 2"],
    "Group 3": ["Group 1", "Group 2", "Group 3"],
    "Group 4": ["Group 1", "Group 2", "Group 3", "Group 4"]
}

def load_data(file_path):
    xls = pd.ExcelFile(file_path)
    df_priests = xls.parse("Priests")
    df_church = xls.parse("Church")
    df_priests["source_sheet"] = "priest_detail"
    df_church["source_sheet"] = "church_detail"
    return pd.concat([df_priests, df_church], ignore_index=True)

def get_group_instances():
    groups = {}
    for name in GROUP_PRIORITY:
        description = GROUP_DESCRIPTIONS[name]
        group, _ = CryptaGroup.objects.update_or_create(
            name=name,
            defaults={
                "description": description,
                "is_enabled": (name == "Group 1")
            }
        )
        groups[name] = group
    return groups

def build_group_resource_map(df):
    access_map = defaultdict(lambda: defaultdict(set))  # group -> resource_type -> fields

    for _, row in df.iterrows():
        col_name = row.get("ColumnName/Relationship")
        # resource_type = row.get("resource_type")
        resource_type = row.get("relatedTableName")
        if not pd.notna(col_name) or not pd.notna(resource_type):
            continue

        for group_name in reversed(GROUP_PRIORITY):
            if pd.notna(row.get(group_name)):
                allowed_groups = GROUP_HIERARCHY[group_name]
                for g in allowed_groups:
                    access_map[g][resource_type].add(col_name)
                break  # apply only highest priority access level

    return access_map

def main():
    df = load_data(FILE)

    # ⛔ Exclude rows with 'Query' in the field name or 'DROPPED' as the relatedTableName
    df = df.dropna(subset=["ColumnName/Relationship", "relatedTableName"])
    df = df[~df["ColumnName/Relationship"].str.strip().str.lower().eq("query")]
    df = df[~df["relatedTableName"].fillna("").str.strip().str.lower().eq("dropped")]
    
    groups = get_group_instances()
    access_map = build_group_resource_map(df)

    QueryPermission.objects.all().delete()

    with transaction.atomic():
        for group_name, resources in access_map.items():
            group = groups[group_name]
            for resource_type, fields in resources.items():
                QueryPermission.objects.update_or_create(
                    group=group,
                    resource_type=resource_type,
                    access_type="read",
                    defaults={
                        "view_limits": {"fields": sorted(fields)},
                        "filter_conditions": {}
                    }
                )

if __name__ == "__main__":
    main()
