""" This module is only used for storing and handling constant values
used by other modules. """
# Dynamic filter configuration mapping base types to model fields or joins
DYNAMIC_FILTER_FIELDS = {
    'person': [
        # Direct CharFields / choices on Person
        'personType',                # e.g. Priest / Deacon / Lay Person
        'prefix',                    # Mr. / Dr. / Reverend / etc.
        'residencyType',             # Your residencyType field
        'activeOutsideDOC',          # Active outside DOC choices
        'legalStatus',               # Legal status choices

        # Boolean
        'is_safeEnvironmentTraining',  # True / False

        # DateFields
        'date_baptism',              # Baptism date
        'date_deceased',             # Deceased date
        'date_retired',              # Retirement date

        # ForeignKey → Address (residence & mailing)
        'lkp_residence_id__city',    # Residence city
        'lkp_residence_id__state',   # Residence state 
        'lkp_mailing_id__city',      # Mailing address city
        'lkp_mailing_id__state',     # Mailing state 

        # Reverse rel’n from Assignment
        'assignment__lkp_assignmentType_id__title',   # Assignment type title
        'assignment__lkp_location_id__name',          # Location name from assignments
        'assignment__lkp_location_id__lkp_vicariate_id__name', # Vicariate Assignment
        'assignment__date_assigned',                  # Assignment date

        # Reverse rel’n from Person_Status
        'person_status__lkp_status_id__name',         # Status name
        'person_status__date_assigned',               # When status assigned
    ],
    'location': [
        'type',                                   # Location type (Church / School / etc.)
        'lkp_physicalAddress_id__city',           # Physical address city 
        'lkp_mailingAddress_id__city',            # Mailing address city 
        'lkp_vicariate_id__name',                 # Vicariate name 
        'lkp_county_id__name',                    # Country name
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
        'lkp_county_id__name':                          'County'
        
}