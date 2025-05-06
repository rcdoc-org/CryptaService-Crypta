import os
import sys
import re
from datetime import datetime
import pandas as pd
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import (
    Location, Address, Vicariate, County, Church_Detail, Language, Church_Language,
    EmailType, Location_Email
)
from django.db import transaction


def import_churches(csv_file):
    """
    Import church data from a CSV file into the database.
    """
    data = pd.read_csv(csv_file)
    
    EMAIL_FIELDS = [
        'EmailClick'
    ]
    EMAIL_DOMAIN_DIOCESAN = [
        'rcdoc.org',
        'charlottediocese.org'
        '4sjnc.org',
        'holyinfantrnc.org',
        'stdorothys.org',
        'stvincentdepaulchurch.com',
        'stmccg.org',
        'staloysiushickory.org',
        'saintmmc.com',
        'stmichaelsgastonia.org',
        'ourladyofmercync.org'
    ]

    with transaction.atomic():
        for _, row in data.iterrows():
            # Create or get physical address
            physical_address, _ = Address.objects.get_or_create(
                address1=row['Physical Address (Street)'],
                city=row['Physical Address (City)'],
                state=row['Physical Address (State)'],
                zip_code=row['Physical Address (Zip Code)'],
                country='USA',  # Assuming all addresses are in the USA
                defaults={'friendlyName': f"{row['Parish']} Physical Address"}
            )

            # Create or get mailing address
            mailing_address, _ = Address.objects.get_or_create(
                address1=row['Mailing Address (Street)'],
                city=row['Mailing Address (City)'],
                state=row['Mailing Address (State)'],
                zip_code=row['Mailing Address (Zip Code)'],
                country='USA',  # Assuming all addresses are in the USA
                defaults={'friendlyName': f"{row['Parish']} Mailing Address"}
            )

            # Create or get vicariate
            vicariate, _ = Vicariate.objects.get_or_create(
                name=row['Vicariate']
            )

            # Create or get county
            county, _ = County.objects.get_or_create(
                name=row['County']
            )

            # Create or get location
            location, _ = Location.objects.get_or_create(
                name=row['Parish Full Name'],
                defaults={
                    'type': 'church',
                    # Handle NaN values for latitude and longitude
                    'latitude': float(row['Latitude']) if pd.notna(row['Latitude']) else None,
                    'longitude': float(row['Longitude']) if pd.notna(row['Longitude']) else None,
                    'website': row.get('Website', None),
                    'lkp_physicalAddress_id': physical_address,
                    'lkp_mailingAddress_id': mailing_address,
                    'lkp_vicariate_id': vicariate,
                    'lkp_county_id': county,
                }
            )
            
            if pd.notna(row.get('EmailClick')):
                email = row.get('EmailClick')
                email = re.sub(r'(?i)^mailto:', '', email.strip())
                _, domain = email.split('@', 1)
                if domain in EMAIL_DOMAIN_DIOCESAN:
                    email_type, _ = EmailType.objects.get_or_create(name='Diocesan')
                    Location_Email.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_emailType_id = email_type,
                        defaults = {
                            'email': email,
                            'is_primary': True,
                        }
                    )
                else:
                    email_type, _ = EmailType.objects.get_or_create(name='Parish')
                    Location_Email.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_emailType_id = email_type,
                        defaults = {
                            'email': email,
                            'is_primary': False,
                        }
                    )

            # Create or get church detail
            Church_Detail.objects.get_or_create(
                lkp_location_id=location,
                defaults={
                    'parishUniqueName': row['Parish Unique Name'],
                    'is_mission': row['Type'].lower() == 'mission',
                    'is_doc': True,  # Assuming all are Diocese of Charlotte
                    'tax_id': row.get('Tax ID', None),
                    'cityServed': row.get('City Served', None),
                    'geo_id': int(float(row['GeoID'])) if pd.notna(row['GeoID']) and not pd.isna(row['GeoID']) else None,
                    'parish_id': row['Parish Number'],
                    'date_established': parse_date(row.get('Established Date')),
                    'date_firstDedication': parse_date(row.get('First Church Dedication Date')),
                    'date_secondDedication': parse_date(row.get('Second Church Dedication Date')),
                }
            )

            # Create or get languages and mass times
            if pd.notna(row.get('Sunday Masses')):
                regex_sundayMass = r'((?:[1-9]|1[0-2]):[0-9]{2} [apAP][mM]) \(([\w-]+)\)|((?:[1-9]|1[0-2]) [apAP][mM]) \(([\w-]+)\)'
                sundayMassTimes = re.findall(regex_sundayMass, row['Sunday Masses'])

                for match in sundayMassTimes:
                    # Determine which capture groups are populated
                    if match[0]:  # First pattern matched
                        mass_time = match[0]
                        language_name = match[1]
                    else:  # Second pattern matched
                        mass_time = match[2]
                        language_name = match[3]

                     # Convert mass_time to 24-hour format
                    try:
                        mass_time_24hr = datetime.strptime(mass_time, "%I:%M %p").time() if ":" in mass_time else datetime.strptime(mass_time, "%I %p").time()
                    except ValueError:
                        print(f"Invalid mass time format: {mass_time}")
                        continue  # Skip this entry if the time format is invalid
        
                    # Create or get the language
                    language, _ = Language.objects.get_or_create(name=language_name.strip())

                    # Create or get the Church_Language entry with massTime
                    Church_Language.objects.get_or_create(
                        lkp_church_id=location,
                        lkp_language_id=language,
                        defaults={'massTime': mass_time_24hr}
                    )

    print("Church data imported successfully.")


def parse_date(date_str):
    """
    Parse a date string in MM/DD/YYYY format to YYYY-MM-DD.
    """
    if pd.notna(date_str):
        try:
            return datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
            print(f"Invalid date format: {date_str}")
    return None


if __name__ == "__main__":
    # Path to the CSV file
    csv_file = '/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/backend/api/Churches (6).csv'

    # Run the import function
    import_churches(csv_file)