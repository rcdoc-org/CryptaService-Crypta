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
    EmailType, Location_Email, Location_Phone, PhoneType, Status,
    Location_Status, Assignment, AssignmentType, Person, Person_Email, Person_Phone
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
        'ourladyofmercync.org',
        'stmarknc.org',
    ]
    
    def parse_bool(value):
        if pd.isna(value):
            return None
        val = str(value).strip().lower()
        return val in ['yes', 'true', '1']

    with transaction.atomic():
        for _, row in data.iterrows():
            # Create or get physical address
            physical_address = None
            if pd.notna(row.get('Physical Address (Street)')):
                physical_address, _ = Address.objects.get_or_create(
                    address1=row['Physical Address (Street)'],
                    city=row['Physical Address (City)'] if pd.notna(row.get('Physical Address (City)')) else 'Missing',
                    state=row['Physical Address (State)'] if pd.notna(row.get('Physical Address (State)')) else 'NC',
                    zip_code=row['Physical Address (Zip Code)'] if pd.notna(row.get('')) else 'Missing',
                    country='US',  # Assuming all addresses are in the USA
                    defaults={'friendlyName': f"{row['Parish Unique Name']} Physical Address"}
                )

            # Create or get mailing address
            mailing_address = None
            if pd.notna(row.get('Mailing Address (Street)')):
                mailing_address, _ = Address.objects.get_or_create(
                    address1=row['Mailing Address (Street)'],
                    city=row['Mailing Address (City)'] if pd.notna(row.get('Mailing Address (City)')) else 'Missing',
                    state=row['Mailing Address (State)'] if pd.notna(row.get('Mailing Address (State)')) else 'NC',
                    zip_code=row['Mailing Address (Zip Code)'] if pd.notna(row.get('Mailing Address (Zip Code)')) else 'Missing',
                    country='US',  # Assuming all addresses are in the USA
                    defaults={'friendlyName': f"{row['Parish Unique Name']} Mailing Address"}
                )
            
            # Create or get rectory address
            rectory_address = None
            if pd.notna(row.get('Rectory Address - Street')):
                rectory_address, _ = Address.objects.get_or_create(
                    address1=row['Rectory Address - Street'],
                    city=row['Rectory Address - City'] if pd.notna(row.get('Rectory Address - City')) else 'Missing',
                    state=row['Rectory Address - State'] if pd.notna(row.get('Rectory Address - State')) else 'NC',
                    zip_code=row['Rectory Address - Zip Code'] if pd.notna(row.get('Rectory Address - Zip Code')) else 'Missing',
                    country='US',  # Assuming all addresses are in the USA
                    defaults={'friendlyName': f"{row['Parish Unique Name']} Rectory Address"}
                )

            # Create or get vicariate
            vicariate = None
            if pd.notna(row.get('Vicariate')):
                vicariate, _ = Vicariate.objects.get_or_create(
                    name=row['Vicariate']
                )

            # Create or get county
            county = None
            if pd.notna(row.get('County')):
                county, _ = County.objects.get_or_create(
                    name=row['County']
                )

            # Create or get location
            location, _ = Location.objects.get_or_create(
                name=row['Parish Unique Name'],
                defaults={
                    'type': 'church',
                    # Handle NaN values for latitude and longitude
                    'latitude': float(row['Latitude']) if pd.notna(row['Latitude']) else None,
                    'longitude': float(row['Longitude']) if pd.notna(row['Longitude']) else None,
                    'website': row.get('Website') if pd.notna(row.get('Website')) else None,
                    'lkp_physicalAddress_id': physical_address,
                    'lkp_mailingAddress_id': mailing_address,
                    'lkp_vicariate_id': vicariate,
                    'lkp_county_id': county,
                }
            )
            
            # Email Connections
            if pd.notna(row.get('EmailClick')):
                email = row.get('EmailClick')
                email = re.sub(r'(?i)^mailto:', '', email.strip())
                _, domain = email.split('@', 1)
                if domain in EMAIL_DOMAIN_DIOCESAN:
                    email_type, _ = EmailType.objects.get_or_create(name='diocesan')
                    Location_Email.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_emailType_id = email_type,
                        defaults = {
                            'email': email,
                            'is_primary': True,
                        }
                    )
                else:
                    email_type, _ = EmailType.objects.get_or_create(name='parish')
                    Location_Email.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_emailType_id = email_type,
                        defaults = {
                            'email': email,
                            'is_primary': False,
                        }
                    )
            
            # Phone Connections
            phone = None
            if pd.notna(row.get('Phone')):
                phone = row.get('Phone')
                phone = re.sub(r'[^0-9]', '', str(phone).strip())
                
                phone_type, _ = PhoneType.objects.get_or_create(name='parish')
                Location_Phone.objects.update_or_create(
                    lkp_location_id=location,
                    lkp_phoneType_id=phone_type,
                    defaults={
                        'phoneNumber': phone,
                        'is_primary': True,  # Assuming the first phone number is primary
                    }
                )
            
            status = None
            if pd.notna(row.get('Status')):
                status = row.get('Status').strip().lower()
                stasus_type, _ = Status.objects.get_or_create(name=status)
                Location_Status.objects.update_or_create(
                    lkp_location_id = location,
                    lkp_status_id = stasus_type,
                    defaults = {
                        'date_assigned': datetime.now(),  # Assuming current date for assignment
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
                    'type': row.get('Type') if pd.notna(row.get('Type')) else 'parish',
                    'seatingCapacity': int(row['Seating Capacity']) if pd.notna(row.get('Seating Capacity')) else 0,
                    'has_homeschoolProgram': parse_bool(row.get('Homeschool Program')),
                    'has_childCareDayCare': parse_bool(row.get('Child care/Day care')),
                    'has_scoutingProgram': parse_bool(row.get('Scouting program')),
                    'has_chapelOnCampus': parse_bool(row.get('Chapel on Campus')),
                    'has_adorationChapelOnCampus': parse_bool(row.get('Adoration Chapel on Campus')),
                    'has_columbarium': parse_bool(row.get('Columbarium')),
                    'has_cemetary': parse_bool(row.get('Cemetery')),
                    'has_schoolOnSite': parse_bool(row.get('School On Site')),
                    'schoolType': row.get('School Type') if pd.notna(row.get('School Type')) else None,
                    'is_nonParochialSchoolUsingFacilities': parse_bool(row.get('Non-parochial School Using Facilities')),
                }
            )
            
            # Assignments Lay people & Creation
            # DRE
            dre = None
            if pd.notna(row.get('DRE')):
                name = row.get('DRE').strip().split(' ')
                first_name = name[0] if len(name) > 0 else ''
                last_name = name[-1] if len(name) > 1 else ''
                middle_name = name[1] if len(name) > 2 else ''
                dre = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                        'is_safeEnvironmentTraining': parse_bool(row.get('DRE Safe Environment Training'))
                    }
                )
                if dre:
                    assign_type, _ = AssignmentType.objects.get_or_create(name='dre')
                    Assignment.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_assignmentType_id = assign_type,
                        lkp_person_id = dre,
                        defaults={
                            'date_assigned': datetime.now(),  # Assuming current date for assignment
                        }
                    )
                if pd.notna(row.get('DRE Email')):
                    email_type, _ = EmailType.objects.get_or_create(name='personal')
                    Person_Email.objects.update_or_create(
                        lkp_person_id = dre,
                        email = row.get('DRE Email') if pd.notna(row.get('DRE Email')) else None,
                        lkp_emailType_id = email_type,
                        defaults={
                            'is_primary': True,  # Assuming the first email is primary
                        }
                    )
                if pd.notna(row.get('DRE Phone%23')):
                    phone_type, _ = PhoneType.objects.get_or_create(name='cell')
                    Person_Phone.objects.update_or_create(
                        lkp_person_id = dre,
                        phoneNumber = re.sub(r'[^0-9]', '', str(row.get('DRE Phone%23')).strip()),
                        lkp_phoneType_id = phone_type,
                        defaults={
                            'is_primary': True,  # Assuming the first phone number is primary
                        }
                    )
                        
            # Youth Minister
            youth_minister = None
            if pd.notna(row.get('Youth Minister')):
                name = row.get('Youth Minister').strip().split(' ')
                first_name = name[0] if len(name) > 0 else ''
                last_name = name[-1] if len(name) > 1 else ''
                middle_name = name[1] if len(name) > 2 else ''
                youth_minister = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                        'is_safeEnvironmentTraining': parse_bool(row.get('YM Safe Environment Training'))
                    }
                )
                if youth_minister:
                    assign_type, _ = AssignmentType.objects.get_or_create(name='youth minister')
                    Assignment.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_assignmentType_id = assign_type,
                        lkp_person_id = youth_minister,
                        defaults={
                            'date_assigned': datetime.now(),  # Assuming current date for assignment
                        }
                    )
                if pd.notna(row.get('YM Email')):
                    email_type, _ = EmailType.objects.get_or_create(name='personal')
                    Person_Email.objects.update_or_create(
                        lkp_person_id = youth_minister,
                        email = row.get('YM Email') if pd.notna(row.get('YM Email')) else None,
                        lkp_emailType_id = email_type,
                        defaults={
                            'is_primary': True,  # Assuming the first email is primary
                        }
                    )
                if pd.notna(row.get('YM Phone%23')):
                    phone_type, _ = PhoneType.objects.get_or_create(name='cell')
                    Person_Phone.objects.update_or_create(
                        lkp_person_id = youth_minister,
                        phoneNumber = re.sub(r'[^0-9]', '', str(row.get('YM Phone%23')).strip()),
                        lkp_phoneType_id = phone_type,
                        defaults={
                            'is_primary': True,  # Assuming the first phone number is primary
                        }
                    )

            # Office Manager
            office_mgr = None
            if pd.notna(row.get('Office Mgr/Parish Contact')):
                name = row.get('Office Mgr/Parish Contact').strip().split(' ')
                first_name = name[0] if len(name) > 0 else ''
                last_name = name[-1] if len(name) > 1 else ''
                middle_name = name[1] if len(name) > 2 else ''
                youth_minister = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                    }
                )
                if office_mgr:
                    assign_type, _ = AssignmentType.objects.get_or_create(name='office mgr')
                    Assignment.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_assignmentType_id = assign_type,
                        lkp_person_id = office_mgr,
                        defaults={
                            'date_assigned': datetime.now(),  # Assuming current date for assignment
                        }
                    )
                if pd.notna(row.get('Office Mgr/Parish Contact Email')):
                    email_type, _ = EmailType.objects.get_or_create(name='personal')
                    Person_Email.objects.update_or_create(
                        lkp_person_id = office_mgr,
                        email = row.get('Office Mgr/Parish Contact Email') if pd.notna(row.get('Office Mgr/Parish Contact Email')) else None,
                        lkp_emailType_id = email_type,
                        defaults={
                            'is_primary': True,  # Assuming the first email is primary
                        }
                    )
            
            # Financial Council Chair
            financial_council_chair = None
            if pd.notna(row.get('Financial Council Chair Name')):
                name = row.get('Financial Council Chair Name').strip().split(' ')
                first_name = name[0] if len(name) > 0 else ''
                last_name = name[-1] if len(name) > 1 else ''
                middle_name = name[1] if len(name) > 2 else ''
                
                fin_address, _ = Address.objects.get_or_create(
                    address1 = row.get('Financial Council Chair Address') if pd.notna(row.get('Financial Council Chair Address')) else 'Missing',
                    address2 = 'Missing',
                    city = 'Missing',
                    state = 'NC',
                    zip_code = 'Missing',
                    country = 'US',  # Assuming all addresses are in the USA
                    defaults={
                        'friendlyName': f"{name} Residence"
                    }
                )
                
                financial_council_chair = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                        'lkp_residence_id': fin_address,
                    }
                )
                if financial_council_chair:
                    assign_type, _ = AssignmentType.objects.get_or_create(name='financial council chair')
                    Assignment.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_assignmentType_id = assign_type,
                        lkp_person_id = financial_council_chair,
                        defaults={
                            'date_assigned': datetime.now(),  # Assuming current date for assignment
                        }
                    )
                if pd.notna(row.get('Financial Council Chair Email')):
                    email_type, _ = EmailType.objects.get_or_create(name='personal')
                    Person_Email.objects.update_or_create(
                        lkp_person_id = financial_council_chair,
                        email = row.get('Financial Council Chair Email') if pd.notna(row.get('Financial Council Chair Email')) else None,
                        lkp_emailType_id = email_type,
                        defaults={
                            'is_primary': True,  # Assuming the first email is primary
                        }
                    )
                if pd.notna(row.get('Financial Council Chair Phone%23')):
                    phone_type, _ = PhoneType.objects.get_or_create(name='cell')
                    Person_Phone.objects.update_or_create(
                        lkp_person_id = financial_council_chair,
                        phoneNumber = re.sub(r'[^0-9]', '', str(row.get('Financial Council Chair Phone%23')).strip()),
                        lkp_phoneType_id = phone_type,
                        defaults={
                            'is_primary': True,  # Assuming the first phone number is primary
                        }
                    )
                    
            # Pastoral Council Chair
            pastoral_council_chair = None
            if pd.notna(row.get('Pastoral Council Chair Name')):
                name = row.get('Pastoral Council Chair Name').strip().split(' ')
                first_name = name[0] if len(name) > 0 else ''
                last_name = name[-1] if len(name) > 1 else ''
                middle_name = name[1] if len(name) > 2 else ''
                
                pas_address, _ = Address.objects.get_or_create(
                    address1 = row.get('Pastoral Council Chair Address') if pd.notna(row.get('Pastoral Council Chair Address')) else 'Missing',
                    address2 = 'Missing',
                    city = 'Missing',
                    state = 'NC',
                    zip_code = 'Missing',
                    country = 'US',  # Assuming all addresses are in the USA
                    defaults={
                        'friendlyName': f"{name} Residence"
                    }
                )
                
                pastoral_council_chair = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                        'lkp_residence_id': pas_address,
                    }
                )
                if pastoral_council_chair:
                    assign_type, _ = AssignmentType.objects.get_or_create(name='pastoral council chair')
                    Assignment.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_assignmentType_id = assign_type,
                        lkp_person_id = pastoral_council_chair,
                        defaults={
                            'date_assigned': datetime.now(),  # Assuming current date for assignment
                        }
                    )
                if pd.notna(row.get('Pastoral Council Chair Email')):
                    email_type, _ = EmailType.objects.get_or_create(name='personal')
                    Person_Email.objects.update_or_create(
                        lkp_person_id = pastoral_council_chair,
                        email = row.get('Pastoral Council Chair Email') if pd.notna(row.get('Pastoral Council Chair Email')) else None,
                        lkp_emailType_id = email_type,
                        defaults={
                            'is_primary': True,  # Assuming the first email is primary
                        }
                    )
                if pd.notna(row.get('Pastoral Council Chair Phone%23')):
                    phone_type, _ = PhoneType.objects.get_or_create(name='cell')
                    Person_Phone.objects.update_or_create(
                        lkp_person_id = pastoral_council_chair,
                        phoneNumber = re.sub(r'[^0-9]', '', str(row.get('Pastoral Council Chair Phone%23')).strip()),
                        lkp_phoneType_id = phone_type,
                        defaults={
                            'is_primary': True,  # Assuming the first phone number is primary
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

def missionOf(csv_file):
   data = pd.read_csv(csv_file) 

   
   with transaction.atomic():
        for _, row in data.iterrows():
            if pd.notna(row.get('Mission Of')):
                # Get the parish location based on 'Mission Of'
                parish_location, _ = Location.objects.get(
                    name = row['Mission Of'],
                )
                # Update the mission of location
                mission_location, _ = Location.objects.update_or_create(
                    name=row['Parish Unique Name'],
                    defaults={
                        'missionOf': parish_location,
                    }
                )

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
    csv_file = '/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/backend/api/data/Churches (6).csv'

    # Run the import function
    import_churches(csv_file)
    missionOf(csv_file)