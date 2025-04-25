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
        'lkp_residence_id__state',   # Residence state (if exists)
        'lkp_mailing_id__city',      # Mailing address city
        'lkp_mailing_id__state',     # Mailing state (if exists)

        # Reverse rel’n from Assignment
        'assignment__lkp_assignmentType_id__title',   # Assignment type title
        'assignment__lkp_location_id__name',          # Location name from assignments
        'assignment__date_assigned',                  # Assignment date (if you want)

        # Reverse rel’n from Person_Status
        'person_status__lkp_status_id__name',         # Status name
        'person_status__date_assigned',               # When status assigned
    ],
    'location': [
        'type',                                   # Location type (Church / School / etc.) :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}
        'lkp_physicalAddress_id__city',           # Physical address city :contentReference[oaicite:4]{index=4}&#8203;:contentReference[oaicite:5]{index=5}
        'lkp_mailingAddress_id__city',            # Mailing address city :contentReference[oaicite:10]{index=10}&#8203;:contentReference[oaicite:11]{index=11}
        'lkp_vicariate_id__name',                 # Vicariate name :contentReference[oaicite:16]{index=16}&#8203;:contentReference[oaicite:17]{index=17}
        'lkp_county_id__name',          # simple field
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