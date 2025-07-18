import os
import sys
import re
from datetime import datetime
import pandas as pd
import django

current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the project root so ``crypta_service`` can be imported when executing this
# script directly.
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypta_service.settings')
django.setup()

from api.models import (
    Location, RegisteredHousehold, Church_Detail
)
from django.db import transaction


def import_registered(excel_file):
    data = pd.read_excel(excel_file)
    print(data.columns.tolist())
    
    with transaction.atomic():
        for _, row in data.iterrows():
            parish_id = int(row['Parish ID'])
            
            try:
                location = Church_Detail.objects.get(parish_id=parish_id).lkp_location_id
            except Church_Detail.DoesNotExist:
                print(f"Skipping parish_id {parish_id}: no Church_Detail found.")
                continue
        
            for year in data.columns[2:]:
                value = row[year]
                if pd.isna(value):
                    continue
            
                RegisteredHousehold.objects.update_or_create(
                    lkp_church_id = location,
                    year = year,
                    defaults={
                        'registeredHouseholds': int(value)
                    }
                )
            
if __name__ == "__main__":
    excel_file = "/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/services/crypta/dataMigration/raw/RegisteredHouseholds.xlsx"
    
    import_registered(excel_file)