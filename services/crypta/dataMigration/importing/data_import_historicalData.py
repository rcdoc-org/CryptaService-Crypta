import os
import sys
import re
from datetime import datetime
import logging
from decimal import Decimal, InvalidOperation
import pandas as pd
import django

logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the project root so ``crypta_service`` can be imported when executing this
# script directly.
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypta_service.settings')
django.setup()

from api.models import (
    StatusAnimarum, BuildingOnSite, SocialOutreachProgram, OctoberMassCount, Location,
    Church_Detail, Ethnicity,
)

from django.db import transaction

def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

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


def import_historical(csv_file):
    
    data = pd.read_csv(csv_file)
    
    BUILDING_COLUMNS = {
        'cemetery':               'DoesTheParishHaveACemetary',
        'columbarium':            'DoesTheParishHaveAColumbarium',
    }

    OUTREACH_COLUMNS = {
        'youth_ministry':         'YouthMinistry',
        'adult_education':        'AdultEducation',
        'adult_sac_prep':         'AdultSacramentalPrep',
    }
    
    for idx, row in data.iterrows():
        with transaction.atomic():
            # 1) pick the best name column & coerce to a clean str
            raw = row.get('Church List Item') or row.get('Name of Parish')
            if pd.isna(raw):
                logger.warning(f"Row {idx}: no church name found, skipping")
                continue

            # normalize whitespace, strip non-breaking spaces, collapse multiples
            church_name = str(raw)\
                .replace('\xa0', ' ')\
                .strip()
            church_name = re.sub(r'\s+', ' ', church_name)

            # 2) safe lookup (or skip if not found)
            try:
                loc = Location.objects.get(name__iexact=church_name)
            except Location.DoesNotExist:
                logger.warning(f"Row {idx}: Location '{church_name}' not in DB, skipping")
                continue
            try:
                church = Church_Detail.objects.get(lkp_location_id=loc)
            except Church_Detail.DoesNotExist:
                print(f"Skipping: No Church_Detail exists for {loc}")
            
            status, _ = StatusAnimarum.objects.update_or_create(
                lkp_church_id = loc,
                year = row['Year'],
                defaults = {
                    # percentages of staff / volunteers
                    'fullTime_deacons':    safe_decimal(row['FullTimeStaffDeacons']),
                    'fullTime_brothers':   safe_decimal(row['FullTimeStaffBrothers']),
                    'fullTime_sisters':    safe_decimal(row['FullTimeStaffSisters']),
                    'fullTime_other':  safe_decimal(row['FullTimeStaffNonClergy']),
                    'partTime_staff':      safe_decimal(row['PartTimeStaff']),
                    'volunteers':         safe_decimal(row['Volunteers']),

                    # BigInteger counts
                    'maxMass':                    safe_int(row['OctoberCount']),

                    # baptisms
                    'baptism_infants':            safe_int(row['BaptismsInfants']),
                    'baptismAge_1_7':             safe_int(row['BaptismsAge1-7']),
                    'baptismAge_8_17':            safe_int(row['BaptismsAge8-17']),
                    'baptismAge_18':              safe_int(row['Baptisms18']),

                    # sacraments & life events
                    'fullCommunionRCIA':          safe_int(row['FullCommRCIA-RCIC']),
                    'firstCommunion':             safe_int(row['1stCommunion']),
                    'confirmation':               safe_int(row['Confirmation']),
                    'marriage_catholic':          safe_int(row['MarriagesCatholic']),
                    'marriage_interfaith':        safe_int(row['MarriagesInterfaith']),
                    'deaths':                     safe_int(row['Deaths']),

                    # faith formation
                    'childrenInFaithFormation': safe_int(row['TotalChildenFaithFormation']),
                    'school_prek_5':                      safe_int(row['PreK5']),
                    'school_grade6_8':            safe_int(row['Grade68']),
                    'school_grade9_12':           safe_int(row['Grade912']),

                    # outreach counts as fields if present
                    'youthMinistry':              safe_int(row['YouthMinistry']),
                    'adult_education':            safe_int(row['AdultEducation']),
                    'adult_sacramentPrep':        safe_int(row['AdultSacramentalPrep']),

                    # catechists
                    'catechist_paid':             safe_int(row.get('CatechistPaid', 0)),
                    'catechist_vol':              safe_int(row.get('CatechistVol', 0)),

                    'referrals_catholicCharities': safe_int(row['ReferralsCatholicCharities']),
                }
            )

            # 2.3 Link up Buildings On Site
            for name, col in BUILDING_COLUMNS.items():
                val = row.get(col, '')
                if str(val).strip().lower() in ('yes', 'y', 'true', '1'):
                    bld, _ = BuildingOnSite.objects.get_or_create(name=name)
                    loc.building_on_site.add(bld)
            
                    if church:
                        if name == 'cemetery':
                            if church.has_cemetary is False:
                                church.has_cemetary = True
                                church.save()
                        if name == 'columbarium':
                            if church.has_columbarium is False:
                                church.has_columbarium = True
                                church.save()

            # 2.4 Link up Outreach Programs (count>0 → has program)
            for name, col in OUTREACH_COLUMNS.items():
                if safe_int(row.get(col, 0)) and safe_int(row[col]) > 0:
                    prog, _ = SocialOutreachProgram.objects.get_or_create(name=name)
                    loc.social_outreach_program.add(prog)
            
            # 2.5 Create an OctoberMassCount row
            if pd.notna(row.get('OctoberCount')) and row.get('OctoberCount') != 0:
                octo_week = safe_int(row['OctoberCount'].replace(',',''))
                octo_week = octo_week / 4
                OctoberMassCount.objects.update_or_create(
                    lkp_church_id=loc,
                    year=row['Year'],
                    defaults={
                        'week1': octo_week,
                        'week2': octo_week,
                        'week3': octo_week,
                        'week4': octo_week,
                    }
                )
            
            # Create Ethnicity
            if pd.notna(row.get('EthnicityOther')):
                Ethnicity.objects.get_or_create(
                    lkp_location_id = loc,
                    year = row['Year'],
                    defaults= {
                        'percent_african': safe_decimal(row.get('EthnicityAfrican', 0)),
                        'percent_africanAmerican': safe_decimal(row.get('EthnicityAfricanAmerican', 0)),
                        'percent_asian': safe_decimal(row.get('EthnicityAsian', 0)),
                        'percent_hispanic': safe_decimal(row.get('EthnicityHispanic', 0)),
                        'percent_americanIndian': safe_decimal(row.get('EthnicityAmericanIndian', 0)),
                        'percent_other': safe_decimal(row.get('EthnicityOther', 0)),
                        'is_censusEstimate': True,
                    }
                )
            
            
    
    
if __name__ == "__main__":
    # Path to the CSV file
    csv_file = '/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/services/crypta/dataMigration/raw/Church Historical Data.csv'

    # Run the import function
    import_historical(csv_file)