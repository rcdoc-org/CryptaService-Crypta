""" This module is only used for storing and handling constant values
used by other modules. """
# Dynamic filter configuration mapping base types to model fields or joins
DYNAMIC_FILTER_FIELDS = {
    'person': [
        # Direct CharFields / choices on Person
        'personType',                # e.g. Priest / Deacon / Lay Person
        'assignment__lkp_location_id__name',          # Location name from assignments
        'assignment__lkp_assignmentType_id__title',   # Assignment type title
        'date_baptism',              # Baptism date
        'is_safeEnvironmentTraining',  # True / False
        'date_deceased',             # Deceased date
        'priest_detail__diocesanReligious',
        'legalStatus',               # Legal status choices
        'activeOutsideDOC',          # Active outside DOC choices
        'lkp_mailing_id__city',      # Mailing address city
        'lkp_mailing_id__state',     # Mailing state 
        'priest_detail__is_massEnglish',
        'priest_detail__is_massSpanish',
        'prefix',                    # Mr. / Dr. / Reverend / etc.
        'residencyType',             # Your residencyType field
        'date_retired',              # Retirement date
        'lkp_residence_id__city',    # Residence city
        'lkp_residence_id__state',   # Residence state 
        'person_status__lkp_status_id__name',         # Status name
        'assignment__date_assigned',                    # Date Assigned
        'assignment__lkp_location_id__lkp_vicariate_id__name', # Vicariate Assignment
    ],
    'location': [
        'type',                                   # Location type (Church / School / etc.)
        'churchDetail_location__cityServed',      # City Served
        'lkp_county_id__name',                    # Country 
        'churchDetail_location__is_doc',           # Diocesan Entity
        'churchDetail_location__is_mission',        # Mission
        'church_language__lkp_language_id__name', #Language Options
        'lkp_physicalAddress_id__city',           # Physical city 
        'lkp_physicalAddress_id__state',           # Physical state 
        'lkp_mailingAddress_id__city',            # Mailing city 
        'lkp_mailingAddress_id__state',            # Mailing city 
        'churchDetail_location__lkp_rectoryAddress_id__city', #Rectory City
        'lkp_vicariate_id__name',                 # Vicariate
    ],
}

FIELD_LABLES = {
    # person Based Filters
   # Direct CharFields / choices on Person
        'personType':                                   'Person Type',
        'prefix':                                       'Prefix',
        'residencyType':                                'Residency Type',
        'activeOutsideDOC':                             'Active Outside DOC',
        'legalStatus':                                  'Legal Status',
        'priest_detail__diocesanReligious':             'Diocesan/Religious',
        'priest_detail__is_massEnglish':                'Mass in English',
        'priest_detail__is_massSpanish':                'Mass in Spanish',

        # Boolean
        'is_safeEnvironmentTraining':                   'Completed Safe Environment Training',

        # DateFields
        'date_baptism':                                 'Baptism Date',
        'date_deceased':                                'Date Deceased',
        'date_retired':                                 'Retirement Date',

        # ForeignKey → Address (residence & mailing)
        'lkp_residence_id__city':                       'Residence: City',
        'lkp_residence_id__state':                      'Residence: State',
        'lkp_mailing_id__city':                         'Mailing: City',
        'lkp_mailing_id__state':                        'Mailing: State',

        # Reverse rel’n from Assignment
        'assignment__lkp_assignmentType_id__title':     'Assignment Type',
        'assignment__lkp_location_id__name':            'Assignment Location',
        'assignment__date_assigned':                    'Status Assigned',
        'assignment__lkp_location_id__lkp_vicariate_id__name':  'Vicariate',
        
        # Reverse rel’n from Person_Status
        'person_status__lkp_status_id__name':           'Status',
        'person_status__date_assigned':                 'Status Assigned',

        # Locations Based Filters
        'type':                                         'Location Type',
        'lkp_physicalAddress_id__city':                 'Physical City',
        'lkp_mailingAddress_id__city':                  'Mailing City',
        'lkp_vicariate_id__name':                       'Vicariate',
        'lkp_county_id__name':                          'County',
        'churchDetail_location__cityServed':                    'City Served',
        'churchDetail_location__is_doc':           'Diocesan Entity',
        'churchDetail_location__is_mission':        'Mission',
        'churchDetail_location__lkp_rectoryAddress_id__city': 'Rectory City',
        'lkp_physicalAddress_id__state':           'Physical State',
        'lkp_mailingAddress_id__state':            'Mailing State', 
        'church_language__lkp_language_id__name': 'Language Options',
        
}