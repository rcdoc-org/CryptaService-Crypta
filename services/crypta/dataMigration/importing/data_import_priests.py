"""Used for large scale data import of priests from a csv file into the database.
This script reads a CSV file containing priest data and imports it into the Django database.
It handles various fields such as personal information, contact details, assignments, and status.
It also manages relationships between different models like Person, Address, DioceseOrder, etc."""
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
    Person, Address, DioceseOrder, Priest_Detail, Vicariate, County,
    EmailType, Person_Email, AssignmentType, Assignment, Location, EasternChurch,
    Status, Person_Status, PhoneType, Person_Phone, Title,
    Person_Title, RelationshipType, Person_Relationship,
)
from django.db import transaction



def import_priests(csv_file):
    """
    Import priest data from a CSV file into the database.
    """
    data = pd.read_csv(csv_file)

    EMAIL_FIELDS = {
        'Personal Email': 'personal',
        'RCDOC Position 1 Email': 'diocesan',
        'RCDOC Other 1 Email': 'parish'
    }
    PHONE_FIELDS = {
        'Cell Phone': 'cell',
        'Preferred Contact Phone %23': 'preferred',
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

    def parse_date(value):
        if pd.notna(value):
            for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None
    
    def parse_bool(value):
        if pd.isna(value):
            return None
        val = str(value).strip().lower()
        return val in ['yes', 'true', '1']

    with transaction.atomic(): 
        for _, row in data.iterrows():
            
            #convert date_birth to YYYY-MM-DD format
            date_birth = parse_date(row.get('Birth Date'))
            date_priestOrdination = parse_date(row.get('Priesthood Ordination Date'))
            date_episcopal = parse_date(row.get('Episcopal Ordination Date'))
            date_transDeacon = parse_date(row.get('Transitional Diaconate Ordination Date'))
            date_extern_start = parse_date(row.get('Extern Priest-Assignment Start Date'))
            date_extern_end = parse_date(row.get('Extern Priest-Assignment End Date'))
            date_baptism = parse_date(row.get('Baptism Date'))
            date_status = parse_date(row.get('Status Date')) if pd.notna(row.get('Status Date')) else datetime.today().date()
            date_retirement = parse_date(row.get('Retirement Date'))
            date_deceased = parse_date(row.get('Deceased Date'))
            date_incardinationRequested = parse_date(row.get('Incardination Request Date'))
            date_incardination = parse_date(row.get('Incardination Date for Current Status'))
            date_facultiesRequested = parse_date(row.get('Faculties Requested Date'))
            date_facultiesGranted = parse_date(row.get('Faculties Granted or Modified Date'))
            
            residence_address = None
            if pd.notna(row.get('Residence Street Address (Line 1)')):
                residence_address, _ = Address.objects.get_or_create(
                    address1=row['Residence Street Address (Line 1)'],
                    address2=row.get('Residence Street Address (Line 2)') if pd.notna(row.get('Residence Street Address (Line 2)')) else None,
                    city=row['Residence City'] if pd.notna(row.get('Residence City')) else 'Missing',
                    state=row['Residence State / Province'] if pd.notna(row.get('Residence State / Province')) else 'NC',
                    zip_code=row['Residence ZIP/Postal Code'] if pd.notna(row.get('Residence ZIP/Postal Code')) else 'Missing',
                    country=row['Residence Country'] if pd.notna(row.get('Residence Country')) else 'US',
                    defaults={'friendlyName': f"{row['Last Name']} Residence"}
                )

            mailing_address = None
            if pd.notna(row.get('Mailing Street Address (Line 1)')):
                mailing_address, _ = Address.objects.get_or_create(
                    address1=row['Mailing Street Address (Line 1)'],
                    address2=row.get('Mailing Street Address (Line 2)') if pd.notna(row.get('Mailing Street Address (Line 2)')) else None,
                    city=row['Mailing Address (City)'] if pd.notna(row.get('Mailing Address (City)')) else 'Missing',
                    state=row['Mailing Address (State / Province)'] if pd.notna(row.get('Mailing Address (State / Province)')) else 'NC',
                    zip_code=row['Mailing Address (ZIP / Postal Code)'] if pd.notna(row.get('Mailing Address (ZIP / Postal Code)')) else 'Missing',
                    country=row['Mailing Address (Country)'] if pd.notna(row.get('Mailing Address (Country)')) else 'US',
                    defaults={'friendlyName': f"{row['Last Name']} Mailing"}
                )

            diocese_order = None
            if pd.notna(row.get('Diocese/Order')):
                diocese_order, _ = DioceseOrder.objects.get_or_create(
                    name=row['Diocese/Order'],
                    defaults={'is_order': row['Diocesan/Religious'] == 'Religious'}
                )
            
            vicariate = None
            if pd.notna(row.get('Vicariate')):
                vicariate, _ = Vicariate.objects.get_or_create(
                    name=row['Vicariate']
                )

            county = None
            if pd.notna(row.get('County')):
                county, _ = County.objects.get_or_create(
                    name=row['County']
                )

            person, _ = Person.objects.get_or_create(
                name_first=row['First Name'],
                name_last=row['Last Name'],
                defaults={
                    'personType': 'priest',
                    'name_middle': row.get('Middle Name', None),
                    'suffix': row.get('Suffix', None),
                    'prefix': row.get('Prefix', None),
                    'residencyType': row.get('Residence Type', None),
                    'activeOutsideDOC': row.get('If Active Outside DOC - Current Assignment', None),
                    'legalStatus': row.get('Legal/Immigration Status', None),
                    'date_birth': date_birth,
                    'lkp_residence_id': residence_address,
                    'lkp_mailing_id': mailing_address,
                    'date_retired': date_retirement,
                    'date_deceased': date_deceased,
                    'date_baptism': date_baptism,
                    'is_paidEmployee': True,
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

            # Phone Connections
            for csv_col, phone_type_name in PHONE_FIELDS.items():
                phone_number = row.get(csv_col)
                if pd.notna(phone_number):
                    phone_number = re.sub(r'[^0-9]', '', str(phone_number).strip()) # Remove non-numeric characters

                    phone_type, _ = PhoneType.objects.get_or_create(name=phone_type_name)
                    Person_Phone.objects.update_or_create(
                        lkp_person_id=person,
                        lkp_phoneType_id=phone_type,
                        defaults={
                            'phoneNumber': phone_number,
                            'is_primary': (csv_col == 'Preferred Contact Phone %23'),
                        }
                    )

            # Status Connections
            if pd.notna(row.get('Status')):
                status_name, _ = Status.objects.get_or_create(
                    name=row.get('Status'),
                    type = 'priest',
                )
                Person_Status.objects.update_or_create(
                    lkp_person_id=person,
                    lkp_status_id=status_name,
                    defaults={
                        'date_assigned': date_status,
                        'details': row.get('Status Details', None),
                    }
                )
            if pd.notna(row.get('Prior Status')):
                prior_status_name, _ = Status.objects.get_or_create(
                    name = row.get('Prior Status'),
                    type = 'priest',
                )
                Person_Status.objects.update_or_create(
                    lkp_person_id=person,
                    lkp_status_id=prior_status_name,
                    defaults={
                        'date_assigned': date_status - pd.Timedelta(days=1),  # Prior status is one day before current
                        'date_released': date_status,
                    }
                )
            
            # Titles
            if pd.notna(row.get('Current Ecclesiastical Offices/Positions')):
                titles = row.get('Current Ecclesiastical Offices/Positions').split(',')
                for title in titles:
                    title = title.strip()
                    title_obj, _ = Title.objects.get_or_create(name=title, is_ecclesiastical=True)
                    if title == 'Vicar Forane':
                        Person_Title.objects.update_or_create(
                            lkp_person_id=person,
                            lkp_title_id=title_obj,
                            defaults={
                                'date_assigned': date_status,
                                'lkp_vicariate_id': vicariate,
                            }
                        )
                    else:
                        Person_Title.objects.update_or_create(
                            lkp_person_id=person,
                            lkp_title_id=title_obj,
                            defaults={
                                'date_assigned': date_status,
                            }
                        )

            # Assignments
            assigned_date = datetime.today().date()
            # Ensure you have an AssignmentType
            # Only creates assignments for church positions.
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
                        }
                    )
            
            # Baptism Location
            baptismLoc = None
            if pd.notna(row.get('Place of Baptism (Parish Name)')) and pd.notna(row.get('Place of Baptism (Street Address)')):
                addr, _ = Address.objects.get_or_create(
                    address1 = row.get('Place of Baptism (Street Address)'),
                    city = row.get('Baptism City', 'Missing'),
                    state = row.get('Baptism State / Province', 'Missing'),
                    zip_code = row.get('Baptism (ZIP / Postal Code', 'Missing'),
                    country = row.get('Baptism Country', 'Missing'),
                    defaults={
                        'friendlyName': row.get('Place of Baptism (Parish Name)')
                    }
                )
                baptismLoc, _ = Location.objects.get_or_create(
                    name = row.get('Place of Baptism (Parish Name)'),
                    defaults={
                        'type': 'church',
                        'lkp_physicalAddress_id': addr,
                    }
                )

            eastern_church = None
            if pd.notna(row.get('Eastern Catholic Church Name')):
                eastern_church, _ = EasternChurch.objects.get_or_create(
                    name = row.get('Eastern Catholic Church Name', None)
                )

            ordination_diocese = None
            if pd.notna(row.get('Ordination Diocese/Order')):
                ordination_diocese, _ = DioceseOrder.objects.get_or_create(
                        name=row.get('Ordination Diocese/Order', None))
            
            incardination_diocese = None
            if pd.notna(row.get('Incardination Diocese/Order')):
                incardination_diocese, _ = DioceseOrder.objects.get_or_create(
                        name=row.get('Incardination Diocese/Order', None))
            
            Priest_Detail.objects.get_or_create(
                lkp_person_id=person,
                defaults={
                    'lkp_dioceseOrder_id': diocese_order,
                    'lkp_residenceDiocese_id': diocese_order,
                    'lkp_placeOfBaptism_id': baptismLoc,
                    'lkp_dioceseOrderOrdination_id': ordination_diocese,
                    'lkp_dioceseOrderIncardination_id': incardination_diocese,
                    'religiousSuffix': row.get('Religious Suffix', None),
                    'diocesanSuffix': row.get('Diocesan Suffix', None),
                    'religiousInstituteType': row.get('Religious Institute Type', None),
                    'religiousOrderProvince': row.get('Religious Order Province', None),
                    'officialCatholicDirectoryStatus': row.get('Official Catholic Directory Status', None),
                    'incardinationHistory': row.get('Incardination History', None),
                    'diocesanReligious': row.get('Diocesan/Religious', None),
                    'is_includeOfficialCatholicDirectory': parse_bool(row.get('Include in Official Catholic Directory?', False)),
                    'is_easternCatholicChurchMember': parse_bool(row.get('Eastern Catholic Church Member?', False)),
                    'is_shareCellPhone': parse_bool(row.get('Ok To Share Cell %23 with Staff?', False)),
                    'is_massEnglish': parse_bool(row.get('Celebrate Mass in English?', False)),
                    'is_massSpanish': parse_bool(row.get('Celebrate Mass in Spanish?', False)),
                    'is_sacramentsEnglish': parse_bool(row.get('Celebrate Other Sacraments in English?', False)),
                    'is_sacramentsSpanish': parse_bool(row.get('Celebrate Other Sacraments in Spanish?', False)),
                    'is_incardinationRequested': parse_bool(row.get('Incardination Requested?', False)),
                    'is_approvedLetterOfGoodStanding': parse_bool(row.get('Approved for Letters of Good Standing?', False)),
                    'is_optedOut_ss_medicare': parse_bool(row.get('Opted out of SS/Medicare (Y/N)', False)),
                    'is_legalWillComplete': parse_bool(row.get('Completed a Legal Will? ', False)),
                    'is_legalWillChanceryFile': parse_bool(row.get('Legal Will in Chancery File?', False)),
                    'is_powerAttorney': parse_bool(row.get('Power of Attorney?', False)),
                    'is_powerAttorneyChanceryFile': parse_bool(row.get('Power of Atty in Chancery File?', False)),
                    'is_backgroundComplete': parse_bool(row.get("Protecting God's Children Status", False)),
                    'notes': row.get('Notes', None),
                    'birth_city': row.get('Birth City', None),
                    'birth_state': row.get('Birth State / Province', None),
                    'birth_country': row.get('Birth Country', None),
                    'date_transitionalDiaconateOrdination': date_transDeacon,
                    'date_priestOrdination': date_priestOrdination,
                    'date_episcopalOrdination': date_episcopal,
                    'date_incardination': date_incardination,
                    'date_incardinationRequested': date_incardinationRequested,
                    'date_facultiesRequested': date_facultiesRequested,
                    'date_facultiesGranted': date_facultiesGranted,
                    'date_externPriestAssignmentStart': date_extern_start,
                    'date_externPriestAssignmentEnd': date_extern_end,
                    'date_baptism': date_baptism,
                    'priestCode': int(row.get('Priest Code')) if pd.notna(row.get('Priest Code')) else None,
                    'misconduct': row.get('Misconduct', None),
                    'otherSkillsCompentencies': row.get('Other Skills/Competencies', None),
                }
            )

            # Emergency Contact 1
            emergency1 = None
            if pd.notna(row.get('Emergency Contact 1: First Name ')):
                emerg_address = None
                if pd.notna(row.get('Emergency Contact 1: Street Address (Line 1)')):
                    emerg_address, _ = Address.objects.get_or_create(
                        address1=row['Emergency Contact 1: Street Address (Line 1)'],
                        address2=row.get('Emergency Contact 1: Street Address (Line 2)') if pd.notna(row.get('Emergency Contact 1: Street Address (Line 2)')) else None,
                        city=row['Emergency Contact 1: Address City'] if pd.notna(row.get('Emergency Contact 1: Address City')) else 'Missing',
                        state=row['Emergency Contact 1: State / Province'] if pd.notna(row.get('Emergency Contact 1: State / Province')) else 'Missing',
                        zip_code=row['Emergency Contact 1: ZIP / Postal Code'] if pd.notna(row.get('Emergency Contact 1: ZIP / Postal Code')) else 'Missing',
                        country=row['Emergency Contact 1: Country'] if pd.notna(row.get('Emergency Contact 1: Country')) else 'Missing',
                        defaults={
                            'friendlyName': f"{row['Emergency Contact 1: First Name ']} {row['Emergency Contact 1: Last Name ']} Residence",
                        }
                    )
                if emerg_address:
                    emergency1, _ = Person.objects.get_or_create(
                        name_first = row['Emergency Contact 1: First Name '],
                        name_last = row['Emergency Contact 1: Last Name '],
                        defaults={
                            'lkp_residence_id': emerg_address,
                            'personType': 'lay',
                        }
                    )
                else:
                    emergency1, _ = Person.objects.get_or_create(
                        name_first = row['Emergency Contact 1: First Name '],
                        name_last = row['Emergency Contact 1: Last Name '],
                        defaults={
                            'personType': 'lay',
                        }
                        
                    )
                if pd.notna(row.get('Emergency Contact 1: Primary Phone Number ')):
                    phoneType, _ = PhoneType.objects.get_or_create(name='preferred')
                    Person_Phone.objects.update_or_create(
                        lkp_person_id=emergency1,
                        lkp_phoneType_id=phoneType,
                        defaults={
                            'phoneNumber': re.sub(r'[^0-9]', '', str(row['Emergency Contact 1: Primary Phone Number ']).strip()),
                            'is_primary': True,
                        }
                    )
                if pd.notna(row.get('Emergency Contact 1: Secondary Phone Number ')):
                    phoneType, _ = PhoneType.objects.get_or_create(name='secondary')
                    Person_Phone.objects.update_or_create(
                        lkp_person_id=emergency1,
                        lkp_phoneType_id=phoneType,
                        defaults={
                            'phoneNumber': re.sub(r'[^0-9]', '', str(row['Emergency Contact 1: Primary Phone Number ']).strip()),
                            'is_primary': False,
                        }
                    )
                if pd.notna(row.get('Emergency Contact 1: Primary Email Address  ')):
                    email_type, _ = EmailType.objects.get_or_create(name='personal')
                    Person_Email.objects.update_or_create(
                        lkp_person_id=emergency1,
                        lkp_emailType_id=email_type,
                        defaults={
                            'email': re.sub(r'(?i)^mailto:', '', str(row['Emergency Contact 1: Primary Email Address  ']).strip()),
                            'is_primary': True,
                        }
                    )
                if pd.notna(row.get('Emergency Contact 1: Secondary Email Address  ')):
                    email_type, _ = EmailType.objects.get_or_create(name='personal')
                    Person_Email.objects.update_or_create(
                        lkp_person_id=emergency1,
                        lkp_emailType_id=email_type,
                        defaults={
                            'email': re.sub(r'(?i)^mailto:', '', str(row['Emergency Contact 1: Primary Email Address  ']).strip()),
                            'is_primary': False,
                        }
                    )
            
            if emergency1:
                # Create relationship for Emergency Contact 1
                relationship_type, _ = RelationshipType.objects.get_or_create(name=row.get('Emergency Contact 1: Relationship ', 'Emergency Contact'))
                Person_Relationship.objects.update_or_create(
                    lkp_firstPerson_id=person,
                    lkp_secondPerson_id=emergency1,
                    lkp_relationshipType_id=relationship_type,
                    defaults={
                        'is_emergencyContact': True,
                    }
                )
                
                    
            # Emergency Contact 2
            emergency2 = None
            if pd.notna(row.get('Emergency Contact 2: First Name ')):
                emerg_address = None
                if pd.notna(row.get('Emergency Contact 2: Street Address (Line 1)')):
                    emerg_address, _ = Address.objects.get_or_create(
                        address1=row['Emergency Contact 2: Street Address (Line 1)'],
                        address2=row.get('Emergency Contact 2: Street Address (Line 2)') if pd.notna(row.get('Emergency Contact 2: Street Address (Line 2)')) else None,
                        city=row['Emergency Contact 2: Address City'] if pd.notna(row.get('Emergency Contact 2: Address City')) else 'Missing',
                        state=row['Emergency Contact 2: State / Province'] if pd.notna(row.get('Emergency Contact 2: State / Province')) else 'Missing',
                        zip_code=row['Emergency Contact 2: ZIP / Postal Code'] if pd.notna(row.get('Emergency Contact 2: ZIP / Postal Code')) else 'Missing',
                        country=row['Emergency Contact 2: Country'] if pd.notna(row.get('Emergency Contact 2: Country')) else 'Missing',
                        defaults={
                            'friendlyName': f"{row['Emergency Contact 2: First Name ']} {row['Emergency Contact 2: Last Name ']} Residence",
                        }
                    )
                if emerg_address:
                    emergency2, _ = Person.objects.get_or_create(
                        name_first = row['Emergency Contact 1: First Name '],
                        name_last = row['Emergency Contact 1: Last Name '],
                        defaults={
                            'lkp_physical'
                        }
                    )
                else:
                    emergency1, _ = Person.objects.get_or_create(
                        name_first = row['Emergency Contact 1: First Name '],
                        name_last = row['Emergency Contact 1: Last Name '],
                        defaults={
                            'lkp_residence_id': emerg_address,
                            'personType': 'lay',
                        }
                        
                    )
                if pd.notna(row.get('Emergency Contact 1: Primary Phone Number ')):
                    Person_Phone.objects.update_or_create(
                        lkp_person_id=emergency1,
                        lkp_phoneType_id=PhoneType.objects.get(name='preferred'),
                        defaults={
                            'phone': re.sub(r'[^0-9]', '', str(row['Emergency Contact 1: Primary Phone Number ']).strip()),
                            'is_primary': True,
                        }
                    )
                if pd.notna(row.get('Emergency Contact 1: Secondary Phone Number ')):
                    Person_Phone.objects.update_or_create(
                        lkp_person_id=emergency1,
                        lkp_phoneType_id=PhoneType.objects.get(name='secondary'),
                        defaults={
                            'phone': re.sub(r'[^0-9]', '', str(row['Emergency Contact 1: Primary Phone Number ']).strip()),
                            'is_primary': False,
                        }
                    )
                if pd.notna(row.get('Emergency Contact 1: Primary Email Address  ')):
                    Person_Email.objects.update_or_create(
                        lkp_person_id=emergency1,
                        lkp_emailType_id=EmailType.objects.get(name='personal'),
                        defaults={
                            'email': re.sub(r'(?i)^mailto:', '', str(row['Emergency Contact 1: Primary Email Address  ']).strip()),
                            'is_primary': True,
                        }
                    )
                if pd.notna(row.get('Emergency Contact 1: Secondary Email Address  ')):
                    Person_Email.objects.update_or_create(
                        lkp_person_id=emergency1,
                        lkp_emailType_id=EmailType.objects.get(name='personal'),
                        defaults={
                            'email': re.sub(r'(?i)^mailto:', '', str(row['Emergency Contact 1: Primary Email Address  ']).strip()),
                            'is_primary': False,
                        }
                    )
                
            if emergency2:
                # Create relationship for Emergency Contact 1
                relationship_type, _ = RelationshipType.objects.get_or_create(name=row.get('Emergency Contact 2: Relationship ', 'Emergency Contact'))
                Person_Relationship.objects.update_or_create(
                    lkp_firstPerson_id=person,
                    lkp_secondPerson_id=emergency2,
                    lkp_relationshipType_id=relationship_type,
                    defaults={
                        'is_emergencyContact': True,
                    }
                )
                
    

    print("Priest data imported successfully.")

if __name__ == "__main__":
    # Path to the CSV file
    csv_file = '/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/services/crypta/dataMigration/raw/Priests(1).csv'

    # Run the import function
    import_priests(csv_file)