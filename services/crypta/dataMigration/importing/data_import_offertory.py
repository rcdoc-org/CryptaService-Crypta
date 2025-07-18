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
    Location, Offertory, Church_Detail
)
from django.db import transaction


def import_offertory(excel_file):
    data = pd.read_excel(excel_file, header=3)
    print(data.columns.tolist())

    year_map = {
        '7/1/2023 - 6/30/2024': '2023-2024',
        '7/1/2022 - 6/30/2023': '2022-2023',
        '7/1/2021 - 6/30/2022': '2021-2022'
    }
    
    with transaction.atomic():
        for _, row in data.iterrows():
            parish_number = row.get('Parish Number')
            
            if pd.isna(parish_number):
                print(f"Parish Number not found: {parish_number}")
                continue
            
            try:
                church = Church_Detail.objects.get(parish_id=int(parish_number))
                location = church.lkp_location_id
            except Church_Detail.DoesNotExist:
                print(f"Parish Number {parish_number} not found in church_detail.")
                continue

            for column_name, year in year_map.items():
                if column_name in row and not pd.isna(row[column_name]):
                    try:
                        income = int(row[column_name])
                    except ValueError:
                        print(f"Invalid income value for {parish_number} in {year}: {row[column_name]}.")
                        continue
                    
                    Offertory.objects.update_or_create(
                        lkp_church_id = location,
                        year = year,
                        defaults={
                            'income': income,
                        }
                    )
                
            
if __name__ == "__main__":
    excel_file = "/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/services/crypta/dataMigration/raw/OffertoryData.xlsx"
    
    import_offertory(excel_file)