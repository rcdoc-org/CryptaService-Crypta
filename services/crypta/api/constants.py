""" This module is only used for storing and handling constant values
used by other modules. """
# Dynamic filter configuration mapping base types to model fields or joins
DYNAMIC_FILTER_FIELDS = {
    'person': [
        # Direct CharFields / choices on Person
        'personType',                # e.g. Priest / Deacon / Lay Person
        'assignment__lkp_location_id__lkp_county_id__name', # Assignment County
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
        'assignment__lkp_assignmentType_id__title', # Assignments
        'churchDetail_location__cityServed',      # City Served
        'churchDetail_location__has_childCareDayCare', # Child Care Program
        'lkp_county_id__name',                    # Country 
        'churchDetail_location__is_doc',           # Diocesan Entity
        'churchDetail_location__is_mission',        # Mission
        'church_language__lkp_language_id__name', #Language Options
        'lkp_physicalAddress_id__city',           # Physical city 
        'lkp_physicalAddress_id__state',           # Physical state 
        'lkp_mailingAddress_id__city',            # Mailing city 
        'lkp_mailingAddress_id__state',            # Mailing city 
        'churchDetail_location__lkp_rectoryAddress_id__city', #Rectory City
        'social_outreach_program__name',            # Social Outreach Programs
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
        'assignment__lkp_location_id__lkp_county_id__name': 'Assignment County',
        
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
        'social_outreach_program__name':            'Social Outreach Programs',
        'churchDetail_location__has_childCareDayCare': 'Child Care Program',
    
        
}

RELETIVE_RELATIONS = {
    # Person sub-resources
    'priest_detail': 'person',
    'deacon_detail': 'person',
    'lay_detail': 'person',
    'assignment': 'person',
    'person_email': 'person',
    'person_phone': 'person',
    'person_language': 'person',
    'person_facultiesGrantedModified': 'person',
    'person_degreeCertificate': 'person',
    'person_status': 'person',
    'person_title': 'person',
    'person_relationship': 'person',
    'assignments': 'person',
    
    
    # Location sub-resources
    'church_detail': 'location',
    'school_detail': 'location',
    'location_email': 'location',
    'location_phone': 'location',
    'location_status': 'location',
    'statusAnimarum': 'location',
    'registeredHousehold': 'location',
    'ethnicity': 'location',
    'offertory': 'location',
    'octoberMassCount': 'location',
    'buildingsOnSite': 'location',
    'socialOutreachProgram': 'location',
    'church_language': 'location',
    'campusMinistry_detail': 'location',
    'campusMinistry_language': 'location',
    'hospital_detail': 'location',
    'otherEntity_detail': 'location',
    'enrollment': 'location',
    'mission_connections': 'location',
    'assignments': 'location',
    'person_email': 'location',
    'person_phone': 'location',
    'person': 'location',
    
}

DISPLAY_TO_PATH = {
    "# Deacons":  'statusAnimarum_church__fullTime_deacons',
    "# Brothers":  'statusAnimarum_church__fullTime_brothers',
    "# Sisters":  'statusAnimarum_church__fullTime_sisters',
    "# Lay":  'statusAnimarum_church__fullTime_other',
    "# Staff":  'statusAnimarum_church__partTime_staff',
    "Volunteers":  'statusAnimarum_church__volunteers',
    "Registered Households":  'statusAnimarum_church__registeredHouseholds',
    "Max Mass Size":  'statusAnimarum_church__maxMass',
    "Seating Capacity":  'statusAnimarum_church__seatingCapacity',
    "Baptisms 1-7":  'statusAnimarum_church__baptismAge_1_7',
    "Baptisms 8-17":  'statusAnimarum_church__baptismAge_8_17',
    "Baptisms 18+":  'statusAnimarum_church__baptismAge_18',
    "Full Communion RCIA":  'statusAnimarum_church__fullCommunionRCIA',
    "First Communion":  'statusAnimarum_church__firstCommunion',
    "Confirmation":  'statusAnimarum_church__confirmation',
    "Catholic Marriages":  'statusAnimarum_church__marriage_catholic',
    "Interfaith Marriages":  'statusAnimarum_church__marriage_interfaith',
    "Deaths":  'statusAnimarum_church__deaths',
    "Children in Faith Formation":  'statusAnimarum_church__childrenInFaithFormation',
    "Kids: PreK - 5":  'statusAnimarum_church__school_prek_5',
    "Kids: 6-8":  'statusAnimarum_church__school_grade6_8',
    "Kids: 9-12":  'statusAnimarum_church__school_grade9_12',
    "Youth Ministy":  'statusAnimarum_church__youthMinistry',
    "Adult Education":  'statusAnimarum_church__adult_education',
    "Adult Sacrament Prep":  'statusAnimarum_church__adult_sacramentPrep',
    "# Paid Catechists":  'statusAnimarum_church__catechist_paid',
    "# Volunteer Catechists":  'statusAnimarum_church__catechist_vol',
    "RCIA/RCIC":  'statusAnimarum_church__rcia_rcic',
    "# Volunteers Youth":  'statusAnimarum_church__volunteersWorkingYouth',
    "% African":  'statusAnimarum_church__percent_african',
    "% African-American":  'statusAnimarum_church__percent_africanAmerican',
    "% Asian":  'statusAnimarum_church__percent_asian',
    "% Hispanic":  'statusAnimarum_church__percent_hispanic',
    "% American-Indian":  'statusAnimarum_church__percent_americanIndian',
    "% Other":  'statusAnimarum_church__percent_other',
    "Estimate Census?":  'statusAnimarum_church__is_censusEstimate',
    "# Referrals to Catholic Charities":  'statusAnimarum_church__referrals_catholicCharities',
    "HomeSchool Program?":  'statusAnimarum_church__has_homeschoolProgram',
    "Child Care Day Care?":  'statusAnimarum_church__has_chileCareDayCare',
    "Scouting Program?":  'statusAnimarum_church__has_scoutingProgram',
    "Chapel on Campus?":  'statusAnimarum_church__has_chapelOnCampus',
    "Adoration Chapel on Campus?":  'statusAnimarum_church__has_adorationChapelOnCampus',
    "Columbarium on Site?":  'statusAnimarum_church__has_columbarium',
    "Cemetery on Site?":  'statusAnimarum_church__has_cemetary',
    "School on Site?":  'statusAnimarum_church__has_schoolOnSite',
    "NonParochial School Using Facilities?":  'statusAnimarum_church__is_nonParochialSchoolUsingFacilities',
    'Offertory':            'offertory_church__income',
    'October Mass Count':   'octoberCount_church__week1'
}

FIELD_CATEGORIES = {
    # PERSON ONLY
    # — Primary Info —
    "Full Name":          "Primary Info",
    "Person Type":        "Primary Info",
    "Retirement Date":    "Primary Info",
    "Deceased Date":      "Primary Info",
    "Status History":     "Primary Info",
    "Titles":             "Primary Info",
    "Assignments":        "Primary Info",
    "Diocesan/Religious":      "Primary Info",
    
    
    # - Contact Info -
    "Residence Addr":     "Contact Info",
    "Residence City":     "Contact Info",
    "Residence State":     "Contact Info",
    "Residence Zip Code":     "Contact Info",
    "Residence Country":     "Contact Info",
    "Mailing Address":       "Contact Info",
    "Mailing City":       "Contact Info",
    "Mailing State":       "Contact Info",
    "Mailing Zip Code":       "Contact Info",
    "Mailing Country":       "Contact Info",
    "Personal Emails":    "Contact Info",
    "Parish Emails":      "Contact Info",
    "Diocesan Emails":    "Contact Info",
    "Cell Phones":        "Contact Info",
    "Home Phones":        "Contact Info",
    
    
    # - Birth/Sacraments - 
    "Birth Date":         "Birth/Sacraments",
    "Baptism Date":       "Birth/Sacraments",
    "Priest Ordination":      "Birth/Sacraments",
    "Place of Baptism":        "Birth/Sacraments",
    "Birth (City,State)":      "Birth/Sacraments",
    
    
    # - Standing in Diocese - 
    "Safe Env Trng":      "Standing in Diocese",
    "Paid Employee":      "Standing in Diocese",
    "Is Priest?":         "Standing in Diocese",
    "Is Deacon?":         "Standing in Diocese",
    "Is Lay?":            "Standing in Diocese",
    'Ecclesiastical Offices': "Standing in Diocese",
    
    
    # - Degrees/Skills/Lang -
    "Languages":          "Degrees/Skills/Lang",
    "Degrees":            "Degrees/Skills/Lang",
    "Faculties Grants":   "Degrees/Skills/Lang",
    
    
    # - Formation - 
    
    
    # - Name Details -
    "First Name":         "Name Details",
    "Middle Name":        "Name Details",
    "Last Name":          "Name Details",
    "Prefix":             "Name Details",
    "Suffix":             "Name Details",
    
    
    # - Emergency Info -
    "Relationships":      "Emergency Info",
    "Priest Notes":            "Emergency Info",
    

    # LOCATION ONLY
    # - Primary Info - 
    "Name":            "Primary Info",
    "Type":            "Primary Info",
    "Vicariate":       "Primary Info",
    "County":          "Primary Info",
    "Website":         "Primary Info",
    "Emails":          "Primary Info",
    "Phones":          "Primary Info",
    "Parish Name":     "Primary Info",
    "Is Mission":      "Primary Info",
    "City Served":     "Primary Info",
    "Date Established":"Primary Info",
    "First Dedication":"Primary Info",
    "Second Dedication":"Primary Info",
    "Missions":       "Primary Info",
    "Parishes":       "Primary Info",
    
    
    # - Location Info -
    "Physical Addr":   "Location Info",
    "Mailing Addr":     "Location Info",
    "Boundary File":   "Location Info",
    "Church Notes":    "Location Info",
    "School Code":          "Location Info",
    "School Type":          "Location Info",
    "Grade Levels":         "Location Info",
    "Affiliated Parish":    "Location Info",
    "MACS School":          "Location Info",
    "Canonical Status":     "Location Info",
    "Chapel on Site":       "Location Info",
    
    
    # - Clergy - 
    
    
    # - Masses/Ministry - 
    "Mass Languages":          "Masses/Ministries",
    "Campus Mass At Parish":   "Masses/Ministries",
    "Served By":               "Masses/Ministries",
    "Mass Schedule":           "Masses/Ministries",
    "Hours":                   "Masses/Ministries",
    "Facility Type":           "Masses/Ministries",
    "Diocese":                 "Masses/Ministries",
    "Parish Boundary":         "Masses/Ministries",
    "Is Other Entity":         "Masses/Ministries",
    "Social Outreach Programs": "Masses/Ministries",
    
    
    # - Staff -
    "Priests Teaching":     "Staff",
    "Brothers Teaching":    "Staff",
    "Sisters Teaching":     "Staff",
    "Lay Staff Teaching":   "Staff",
    "# Deacons":          "Staff",
    "# Brothers":         "Staff",
    "# Sisters":          "Staff",
    "# Lay":              "Staff",
    "# Staff":            "Staff",
    "# Volunteers":                 "Staff",
    
    
    # - Statistics - 
    "Registered Households":        "Statistics",
    "Max Mass Size":                "Statistics",
    "Seating Capacity":             "Statistics",
    "Baptisms 1-7":                 "Statistics",
    "Baptisms 8-17":                "Statistics",
    "Baptisms 18+":                 "Statistics",
    "Full Communion RCIA":          "Statistics",
    "First Communion":              "Statistics",
    "Confirmation":                 "Statistics",
    "Catholic Marriages":           "Statistics",
    "Interfaith Marriages":         "Statistics",
    "Deaths":                       "Statistics",
    "Children in Faith Formation":  "Statistics",
    "Kids: PreK - 5":               "Statistics",
    "Kids: 6-8":                    "Statistics",
    "Kids: 9-12":                   "Statistics",
    "Youth Ministy":                "Statistics",
    "Adult Education":              "Statistics",
    "Adult Sacrament Prep":         "Statistics",
    "# Paid Catechists":            "Statistics",
    "# Volunteer Catechists":       "Statistics",
    "RCIA/RCIC":                    "Statistics",
    "# Volunteers Youth":           "Statistics",
    "% African":                    "Statistics",
    "% African-American":           "Statistics",
    "% Asian":                      "Statistics",
    "% Hispanic":                   "Statistics",
    "% American-Indian":            "Statistics",
    "% Other":                      "Statistics",
    "Volunteers":                 "Statistics",
    "Estimate Census?":             "Statistics",
    "# Referrals to Catholic Charities":            "Statistics",
    "HomeSchool Program?":          "Statistics",
    "Child Care Day Care?":         "Statistics",
    "Scouting Program?":            "Statistics",
    "Chapel on Campus?":            "Statistics",
    "Adoration Chapel on Campus?":  "Statistics",
    "Columbarium on Site?":         "Statistics",
    "Cemetery on Site?":            "Statistics",
    "School on Site?":              "Statistics",
    "NonParochial School Using Facilities?":        "Statistics",
    "Priest Count":     "Statistics",
    "Offertory":        "Statistics",
    'October Mass Count': 'Statistics',
    
}