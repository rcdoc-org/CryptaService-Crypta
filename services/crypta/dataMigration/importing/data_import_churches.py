import os
import sys
import re
import ast # Required for string list conversion, social outreach programs
from datetime import datetime
from decimal import Decimal, InvalidOperation
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
    Location, Address, Vicariate, County, Church_Detail, Language, Church_Language,
    EmailType, Location_Email, Location_Phone, PhoneType, Status,
    Location_Status, Assignment, AssignmentType, Person, Person_Email, Person_Phone,
    SocialOutreachProgram, Ethnicity
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
    
    def safe_decimal(val):
        # catch pandas NaN, empty or non-numeric
        try:
            # pd.isna will be True for float('nan'), None, pd.NA, etc.
            if pd.isna(val):
                return Decimal('0.0')
            s = str(val).strip()
            # also guard stray empty‐string or literal ‘nan’
            if not s or s.lower() in ('nan', 'na'):
                return Decimal('0.0')
            return Decimal(s)
        except (InvalidOperation, TypeError, ValueError):
            return Decimal('0.0')

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
                stasus_type, _ = Status.objects.get_or_create(name=status, type='location')
                Location_Status.objects.update_or_create(
                    lkp_location_id = location,
                    lkp_status_id = stasus_type,
                    defaults = {
                        'date_assigned': datetime.now(),  # Assuming current date for assignment
                    }
                )
                
            # Set Seating Capacity
            seating_capacity = 0
            if pd.notna(row.get('Seating Capacity')):
                seating_capacity = int(row['Seating Capacity'].replace(',','')) if pd.notna(row.get('Seating Capacity')) else 0
            
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
                    'seatingCapacity': seating_capacity,
                    'has_homeschoolProgram': parse_bool(row.get('Homeschool Program')) if pd.notna(row.get('Homeschool Program')) else False,
                    'has_childCareDayCare': parse_bool(row.get('Child care/Day care')) if pd.notna(row.get('Child care/Day care')) else False,
                    'has_scoutingProgram': parse_bool(row.get('Scouting program')) if pd.notna(row.get('Scouting program')) else False,
                    'has_chapelOnCampus': parse_bool(row.get('Chapel on Campus')) if pd.notna(row.get('Chapel on Campus')) else False,
                    'has_adorationChapelOnCampus': parse_bool(row.get('Adoration Chapel on Campus')) if pd.notna(row.get('Adoration Chapel on Campus')) else False,
                    'has_columbarium': parse_bool(row.get('Columbarium')) if pd.notna(row.get('Columbarium')) else False,
                    'has_cemetary': parse_bool(row.get('Cemetery')) if pd.notna(row.get('Cemetery')) else False,
                    'has_schoolOnSite': parse_bool(row.get('School On Site')) if pd.notna(row.get('School On Site')) else False,
                    'schoolType': row.get('School Type') if pd.notna(row.get('School Type')) else None,
                    'is_nonParochialSchoolUsingFacilities': parse_bool(row.get('Non-parochial School Using Facilities')),
                    'lkp_rectoryAddress_id': rectory_address,
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
                dre, _ = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                        'is_safeEnvironmentTraining': parse_bool(row.get('DRE Safe Environment Training'))
                    }
                )
                if dre:
                    assign_type, _ = AssignmentType.objects.get_or_create(title='dre', personType='lay')
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
                youth_minister, _ = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                        'is_safeEnvironmentTraining': parse_bool(row.get('YM Safe Environment Training'))
                    }
                )
                if youth_minister:
                    assign_type, _ = AssignmentType.objects.get_or_create(title='youth minister', personType='lay')
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
                office_mgr, _ = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                    }
                )
                if office_mgr:
                    assign_type, _ = AssignmentType.objects.get_or_create(title='office mgr', personType='lay')
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
                        'friendlyName': f"{" ".join(name)} Residence"
                    }
                )
                
                financial_council_chair, _ = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                        'lkp_residence_id': fin_address,
                    }
                )
                if financial_council_chair:
                    assign_type, _ = AssignmentType.objects.get_or_create(title='financial council chair', personType='lay')
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
                        'friendlyName': f"{" ".join(name)} Residence"
                    }
                )
                
                pastoral_council_chair, _ = Person.objects.get_or_create(
                    name_first = first_name,
                    name_last = last_name,
                    name_middle = middle_name if middle_name else None,
                    defaults={
                        'personType': 'lay',
                        'lkp_residence_id': pas_address,
                    }
                )
                if pastoral_council_chair:
                    assign_type, _ = AssignmentType.objects.get_or_create(title='pastoral council chair', personType='lay')
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
                mass_text= row.get('Sunday Masses')
                saturday, sunday = '', ''
                if 'Saturday' in mass_text and 'Sunday' in mass_text:
                    parts = mass_text.split('Sunday', 1)
                    saturday = parts[0]
                    sunday = parts[1]
                elif 'Saturday' in mass_text and 'Sunday' not in mass_text:
                    saturday = mass_text
                elif 'Sunday' in mass_text and 'Saturday' not in mass_text:
                    sunday = mass_text
                
                regex_sundayMass = r'((?:[1-9]|1[0-2]):[0-9]{2} [apAP][mM]) *\(([\w\s-]+)\)|((?:[1-9]|1[0-2]) [apAP][mM]) *\(([\w\s-]+)\)'
                sundayMassTimes = re.findall(regex_sundayMass, sunday)
                saturdayMassTimes = re.findall(regex_sundayMass, saturday)
                
                for match in saturdayMassTimes:
                    # Determine which capture groups are populated
                    mass_time = match[0] or match[2]
                    language_name = match[1] or match[3]

                     # Convert mass_time to 24-hour format
                    try:
                        mass_time_24hr = datetime.strptime(mass_time, "%I:%M %p").time() if ":" in mass_time else datetime.strptime(mass_time, "%I %p").time()
                    except ValueError:
                        print(f"Invalid mass time format: {mass_time}")
                        continue  # Skip this entry if the time format is invalid
        
                    # Create or get the language
                    language, _ = Language.objects.get_or_create(name=language_name.strip().lower())

                    # Create or get the Church_Language entry with massTime
                    church_lang, created = Church_Language.objects.get_or_create(
                        lkp_church_id=location,
                        lkp_language_id=language,
                        massTime = mass_time_24hr,
                        massDay = 'sat',
                    )
                    if not created:
                        church_lang.massTime = mass_time_24hr
                        church_lang.save()
                        
                for match in sundayMassTimes:
                    # Determine which capture groups are populated
                    mass_time = match[0] or match[2]
                    language_name = match[1] or match[3]

                     # Convert mass_time to 24-hour format
                    try:
                        mass_time_24hr = datetime.strptime(mass_time, "%I:%M %p").time() if ":" in mass_time else datetime.strptime(mass_time, "%I %p").time()
                    except ValueError:
                        print(f"Invalid mass time format: {mass_time}")
                        continue  # Skip this entry if the time format is invalid
        
                    # Create or get the language
                    language, _ = Language.objects.get_or_create(name=language_name.strip().lower())

                    # Create or get the Church_Language entry with massTime
                    church_lang, created = Church_Language.objects.get_or_create(
                        lkp_church_id=location,
                        lkp_language_id=language,
                        massTime = mass_time_24hr,
                        massDay = 'sun',
                    )
                    if not created:
                        church_lang.massTime = mass_time_24hr
                        church_lang.save()
                
            
            # Create Ethnicity
            if pd.notna(row.get('Ethnicity-Census or Estimate')):
                Ethnicity.objects.get_or_create(
                    lkp_location_id = location,
                    year = str(int(row['Year'])),
                    defaults= {
                        'percent_african': safe_decimal(row.get('Ethnicity-%African', 0)),
                        'percent_africanAmerican': safe_decimal(row.get('Ethnicity-%African-American', 0)),
                        'percent_asian': safe_decimal(row.get('Ethnicity-%Asian', 0)),
                        'percent_hispanic': safe_decimal(row.get('Ethnicity-%Hispanic', 0)),
                        'percent_americanIndian': safe_decimal(row.get('Ethnicity-%American Indian', 0)),
                        'percent_other': safe_decimal(row.get('Ethnicity-%Other', 0)),
                        'is_censusEstimate': True,
                    }
                )

            # Create or get social outreach programs
            programs = None
            if pd.notna(row.get('Social Outreach Services')):
                try:
                    programs = ast.literal_eval(row.get('Social Outreach Services').strip())
                    for name in programs:
                        name = name.strip().lower()
                        program, _ = SocialOutreachProgram.objects.get_or_create(name=name)
                        program.location.add(location)
                except (ValueError, SyntaxError) as e:
                    print(f"Invalid outreach program list format: {row.get('Social Outreach Services')}. Error: {e}")

    print("Church data imported successfully.")

def missionOf(csv_file):
    data = pd.read_csv(csv_file)


    with transaction.atomic():
        for _, row in data.iterrows():
            if pd.notna(row.get('Mission Of')):
                # Get the parish location based on 'Mission Of'
                try:
                    parish_location = Church_Detail.objects.get(parish_id=int(row.get('Mission Of')))
                except Location.DoesNotExist:
                    print(f"Skipping: No church found for Parish_ID {row['Mission Of']}")
                    continue
                # Update the mission of location
                mission_location = Location.objects.get(
                    name=row['Parish Unique Name']
                )
                try:
                    detail = Church_Detail.objects.get(lkp_location_id=mission_location)
                    detail.lkp_missionOf_id = parish_location.lkp_location_id
                    detail.save()
                except Church_Detail.DoesNotExist:
                    print(f"Skipping: No Church_detail exists for {mission_location.name}")

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