import os
import sys
import re
from datetime import datetime
import pandas as pd
import django


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import (
    Person, Address, DioceseOrder, Priest_Detail, Vicariate, County,
    EmailType, Person_Email, AssignmentType, Assignment, Location
)
from django.db import transaction



def import_priests(csv_file):
    """
    Import priest data from a CSV file into the database.
    """
    data = pd.read_csv(csv_file)

    EMAIL_FIELDS = {
        'Personal Email': 'Personal',
        'RCDOC Position 1 Email': 'Diocesan'        
    }
    PARISH_ASSIGNMENT_FIELDS = [
        'Parish 1',
        'Mission 1',
        'Parish 2',
        'Mission 2',
    ]
    PARISH_ASSIGNMENT_TITLES = [
        'Pastor',
        'Parochial Vicar',
        'Parochial Administrator',
        'Priest in Residence',
        'Rector and Pastor',
    ]

    with transaction.atomic(): 
        for _, row in data.iterrows():
            
            #convert date_birth to YYYY-MM-DD format
            date_birth = None
            if pd.notna(row.get('Birth Date')):
                try:
                    date_birth = datetime.strptime(row['Birth Date'], '%m/%d/%Y').strftime('%Y-%m-%d')
                    print(date_birth)
                except ValueError:
                    print(f"Invalid date format for Birth Date: {row['Birth Date']}")
                    continue

            date_ordination = None
            if pd.notna(row.get('Priesthood Ordination Date')):
                try:
                    date_ordination = datetime.strptime(row['Priesthood Ordination Date'], '%m/%d/%Y').strftime('%Y-%m-%d')
                    print(date_ordination)
                except ValueError:
                    print(f"Invalid date format for Ordination Date: {row['Priesthood Ordination Date']}")
                    continue
            
            date_episcopal = None
            if pd.notna(row.get('Episcopal Ordination Date')):
                try:
                    date_episcopal = datetime.strptime(row['Episcopal Ordination Date'], '%m/%d/%Y').strftime('%Y-%m-%d')
                    print(date_episcopal)
                except ValueError:
                    print(f"Invalid date format for Episcopal Date: {row['Episcopal Ordination Date']}")
                    continue
            
            date_transDeacon = None
            if pd.notna(row.get('Transitional Diaconate Ordination Date')):
                try:
                    date_transDeacon = datetime.strptime(row['Transitional Diaconate Ordination Date'], '%m/%d/%Y').strftime('%Y-%m-%d')
                    print(date_transDeacon)
                except ValueError:
                    print(f"Invalid date format for transDeacon Date: {row['Transitional Diaconate Ordination Date']}")
                    continue
            
             
            residence_address, _ = Address.objects.get_or_create(
                address1=row['Residence Street Address (Line 1)'],
                address2=row.get('Residence Street Address (Line 2)', None),
                city=row['Residence City'],
                state=row['Residence State / Province'],
                zip_code=row['Residence ZIP/Postal Code'],
                country=row['Residence Country'],
                defaults={'friendlyName': f"{row['Residence City']} Residence"}
            )

            mailing_address, _ = Address.objects.get_or_create(
                address1=row['Mailing Street Address (Line 1)'],
                address2=row.get('Mailing Street Address (Line 2)', None),
                city=row['Mailing Address (City)'],
                state=row['Mailing Address (State / Province)'],
                zip_code=row['Mailing Address (ZIP / Postal Code)'],
                country=row['Mailing Address (Country)'],
                defaults={'friendlyName': f"{row['Mailing Address (City)']} Mailing"}
            )

            diocese_order, _ = DioceseOrder.objects.get_or_create(
                name=row['Diocese/Order'],
                defaults={'is_order': row['Diocesan/Religious'] == 'Religious'}
            )

            vicariate, _ = Vicariate.objects.get_or_create(
                name=row['Vicariate']
            )

            county, _ = County.objects.get_or_create(
                name=row['County']
            )

            person, _ = Person.objects.get_or_create(
                id=row['ID'],
                defaults={
                    'personType': 'priest',
                    'name_first': row['First Name'],
                    'name_middle': row.get('Middle Name', None),
                    'name_last': row['Last Name'],
                    'suffix': row.get('Suffix', None),
                    'prefix': row.get('Prefix', None),
                    'date_birth': date_birth,
                    'lkp_residence_id': residence_address,
                    'lkp_mailing_id': mailing_address,
                }
            )

            # Emails Connections
            for csv_col, email_type_name in EMAIL_FIELDS.items():
                email_addr = row.get(csv_col)
                if pd.notna(email_addr):
                    email_addr = re.sub(r'(?i)^mailto:', '', email_addr.strip())
                    
                    email_type, _ = EmailType.objects.get_or_create(name=email_type_name)
                    Person_Email.objects.update_or_create(
                        lkp_person_id=person,
                        lkp_emailType_id=email_type,
                        defaults={
                            'email': email_addr,
                            'is_primary': (csv_col == 'RCDOC Position 1 Email'),
                        }
                    )

            # Assignments
            assigned_date = datetime.today().date()
            # Ensure you have an AssignmentType
            if pd.notna(row.get('Position 1')):
                if row.get('Position 1') in PARISH_ASSIGNMENT_TITLES:
                    parish_at, _ = AssignmentType.objects.get_or_create(
                        title = row.get('Position 1'),
                        personType = 'priest'
                    )

            for field in PARISH_ASSIGNMENT_FIELDS:
                loc_name = row.get(field)
                if loc_name and pd.notna(loc_name):
                    loc, _ = Location.objects.get_or_create(name=loc_name, defaults={
                        'type': 'church',
                        'lkp_vicariate_id': vicariate,
                        'lkp_county_id': county,
                    })
                    Assignment.objects.update_or_create(
                        lkp_assignmentType_id = parish_at,
                        lkp_location_id = loc,
                        lkp_person_id = person,
                        defaults={
                            'date_assigned': assigned_date,
                            'term': 1,
                        }
                    )

            Priest_Detail.objects.get_or_create(
                lkp_person_id=person,
                defaults={
                    'lkp_dioceseOrder_id': diocese_order,
                    'lkp_residenceDiocese_id': diocese_order,
                    'lkp_placeOfBaptism_id': None,  # Add logic if baptism location is needed
                    'date_ordination': date_ordination,
                    'date_transitionalDiaconateOrdination': date_transDeacon,
                    'date_episcopalOrdination': date_episcopal,
                    'notes': row.get('Notes', None),
                    'birth_city': row.get('Birth City', None),
                    'birth_state': row.get('Birth State / Province', None),
                    'birth_country': row.get('Birth Country', None),
                }
            )

    print("Priest data imported successfully.")

if __name__ == "__main__":
    # Path to the CSV file
    csv_file = '/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/backend/api/data/Priests (11).csv'

    # Run the import function
    import_priests(csv_file)