import os
import sys
import re
from datetime import datetime
import logging
from decimal import Decimal, InvalidOperation
import pandas as pd
import django

logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import (
    StatusAnimarum, BuildingOnSite, SocialOutreachProgram, OctoberMassCount, Location
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
            
            status, _ = StatusAnimarum.objects.update_or_create(
                lkp_church_id = loc,
                year = row['Year'],
                defaults = {
                    # percentages of staff / volunteers
                    'percentFullTime_deacons':    safe_decimal(row['FullTimeStaffDeacons']),
                    'percentFullTime_brothers':   safe_decimal(row['FullTimeStaffBrothers']),
                    'percentFullTime_sisters':    safe_decimal(row['FullTimeStaffSisters']),
                    'percentFullTime_other':  safe_decimal(row['FullTimeStaffNonClergy']),
                    'percentPartTime_staff':      safe_decimal(row['PartTimeStaff']),
                    'percent_volunteers':         safe_decimal(row['Volunteers']),

                    # BigInteger counts
                    'registeredHouseholds':       safe_int(row['RegisteredHouseholds']),
                    'maxMass':                    safe_int(row['OctoberCount']),
                    'seatingCapacity':            0,  # CSV has no direct field

                    # baptisms
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

                    # demographics
                    'percent_african':            safe_decimal(row['EthnicityAfrican']),
                    'percent_africanAmerican':    safe_decimal(row['EthnicityAfricanAmerican']),
                    'percent_asian':              safe_decimal(row['EthnicityAsian']),
                    'percent_hispanic':           safe_decimal(row['EthnicityHispanic']),
                    'percent_americanIndian':     safe_decimal(row['EthnicityAmericanIndian']),
                    'percent_other':              safe_decimal(row['EthnicityOther']),
                    'is_censusEstimate':          bool(row['EthnicityCensusEstimate']),
                    'referrals_catholicCharities': safe_int(row['ReferralsCatholicCharities']),

                    # on-site facilities
                    'has_cemetary':               (row['DoesTheParishHaveACemetary']=='Yes'),
                    'has_schoolOnSite':           (row['DoesTheParishHaveAColumbarium']=='Yes'),

                    # leave these at defaults or null if not in CSV
                    'schoolType':                 None,
                    'is_nonParochialSchoolUsingFacilities': False,
                }
            )

            # 2.3 Link up Buildings On Site
            for name, col in BUILDING_COLUMNS.items():
                val = row.get(col, '')
                if str(val).strip().lower() in ('yes', 'y', 'true', '1'):
                    bld, _ = BuildingOnSite.objects.get_or_create(name=name)
                    status.building_on_site.add(bld)

            # 2.4 Link up Outreach Programs (count>0 → has program)
            for name, col in OUTREACH_COLUMNS.items():
                if safe_int(row.get(col, 0)) and safe_int(row[col]) > 0:
                    prog, _ = SocialOutreachProgram.objects.get_or_create(name=name)
                    status.social_outreach_program.add(prog)
            
            # 2.5 Create an OctoberMassCount row
            octo_year = int(str(row['Year']).split('-')[0])
            OctoberMassCount.objects.update_or_create(
                lkp_church_id=loc,
                year=octo_year,
                defaults={
                    'week1': safe_int(row['OctoberCount']),
                    'week2': 0,
                    'week3': 0,
                    'week4': 0,
                }
            )
    
    
if __name__ == "__main__":
    # Path to the CSV file
    csv_file = '/Users/kbgreenberg/Documents/Github/CryptaApp/crypta/backend/api/Church Historical Data (2).csv'

    # Run the import function
    import_historical(csv_file)