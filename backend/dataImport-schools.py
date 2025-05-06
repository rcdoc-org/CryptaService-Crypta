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
    SchoolDetail, Location, Enrollment, Assignment, AssignmentType,
    Location_Email, Location_Phone, PhoneType, EmailType,
    Address, Person,
)

from django.db import transaction

def import_schools(csv_file):
    
    data = pd.read_csv(csv_file)
    
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

    for _, row in data.iterrows():
        with transaction.atomic():

            physical_address, _ = Address.objects.get_or_create(
                friendlyName = row['School Name'],
                address1 = row['Street Address'],
                city = row['City'],
                state = row['State Code'],
                zip_code = row['Zip Code'],
                defaults = {
                    'country': 'USA',
                }
            )

            location, _ = Location.objects.get_or_create(
                name = row['School Name'],
                type = 'school',
                latitude = row['Latitude'],
                longitude = row['Longitude'],
                website = row['Web Site'],
                lkp_physicalAddress_id = physical_address,
                lkp_mailingAddress_id = physical_address
            )

            if pd.notna(row.get('School Email')):
                email = row.get('School Email')
                email = re.sub(r'(?i)^mailto:', '', email.strip())
                _, domain = email.split('@', 1)
                if domain in EMAIL_DOMAIN_DIOCESAN:
                    email_type, _ = EmailType.objects.get_or_create(name='Diocesan')
                    Location_Email.objects.update_or_create(
                        lkp_location_id = location,
                        lkp_emailType_id = email_type,
                        defaults = {
                            'email': email,
                            'is_primary': True
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

            phone_type = PhoneType.objects.get(name__iexact='Work')
            Location_Phone.objects.create(
                lkp_location_id = location,
                lkp_phoneType_id = phone_type,
                phoneNumber=str(row['Phone']),
                is_primary = True
            )

            sd = SchoolDetail.objects.get_or_create(
                lkp_location_id = location,
                schoolCode = row['School Code'] if pd.notna(row['School Code']) else 0,
                schoolType=row['School Type'].lower(),
                gradeLevels=row['Grade Levels'].lower(),
                locationType=row['Location'].replace(' ','').lower(),
                sponsorship=row['Sponsorship'].lower(),
                schoolGender=row['School Gender'].lower(),
                is_MACS=row['MACS Flag']=='MACS',
                highSchoolReligiousEd=int(row['High School Religious Ed%23']) if pd.notna(row['High School Religious Ed%23']) else None,
                prek_8religiousEd=int(row['PreK-8th Religious Ed%23']) if pd.notna(row['PreK-8th Religious Ed%23']) else None,
                academicPriest=int(row['Academic Teachers â€“ Priest%23']) if pd.notna(row['Academic Teachers â€“ Priest%23']) else None,
                academicBrother=int(row['Academic Teacher Religious Brothers%23']) if pd.notna(row['Academic Teacher Religious Brothers%23']) else None,
                academicSister=int(row['Academic Teachers Religious Sisters%23']) if pd.notna(row['Academic Teachers Religious Sisters%23']) else None,
                academicLay=int(row['Academic Teachers Paid Lay Persons%23']) if pd.notna(row['Academic Teachers Paid Lay Persons%23']) else None,
                canonicalStatus=row['Canonical Status'],
                is_schoolChapel=row['School Chapel']=='Yes'
            )

            yr = row['Year for which data presented']
            year = f"{yr.split('-')[0]}-{int(yr.split('-')[0])+1}"
            Enrollment.objects.get_or_create(
                lkp_school_id=location,
                year=year,
                prek=int(row['PK/JK Enrollment']) if pd.notna(row['PK/JK Enrollment']) else None,
                transitionalKindergarden=int(row['TK Enrollment']) if pd.notna(row['TK Enrollment']) else None,
                kindergarden=int(row['K Enrollment']) if pd.notna(row['K Enrollment']) else None,
                grade_1=int(row['1st Gr Enrollment']) if pd.notna(row['1st Gr Enrollment']) else None,
                grade_2=int(row['2nd Gr Enrollment']) if pd.notna(row['2nd Gr Enrollment']) else None,
                grade_3=int(row['3rd Gr Enrollment']) if pd.notna(row['3rd Gr Enrollment']) else None,
                grade_4=int(row['4th Gr Enrollment']) if pd.notna(row['4th Gr Enrollment']) else None,
                grade_5=int(row['5th Gr Enrollment']) if pd.notna(row['5th Gr Enrollment']) else None,
                grade_6=int(row['6th Gr Enrollment']) if pd.notna(row['6th Gr Enrollment']) else None,
                grade_7=int(row['7th Gr Enrollment']) if pd.notna(row['7th Gr Enrollment']) else None,
                grade_8=int(row['8th Gr Enrollment']) if pd.notna(row['8th Gr Enrollment']) else None,
                grade_9=int(row['9th Gr Enrollment']) if pd.notna(row['9th Gr Enrollment']) else None,
                grade_10=int(row['10th Gr Enrollment']) if pd.notna(row['10th Gr Enrollment']) else None,
                grade_11=int(row['11th Gr Enrollment']) if pd.notna(row['11th Gr Enrollment']) else None,
                grade_12=int(row['12th Gr Enrollment']) if pd.notna(row['12th Gr Enrollment']) else None
)


if __name__ == "__main__":
    csv_file = '/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/backend/api/schools.csv'

    import_schools(csv_file)
