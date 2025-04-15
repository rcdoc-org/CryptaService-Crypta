from django.db import models

# Create your models here.
class Status(models.Model):
    pass

class EmailType(models.Model):
    pass

class PhoneType(models.Model):
    pass

class Language(models.Model):
    pass

class LanguageProficiency(models.Model):
    pass

class SubjectMatter(models.Model):
    pass

class TypeOfDegree(models.Model):
    pass

class DegreeCertificate(models.Model):
    pass

class RelationshipType(models.Model):
    pass

class Title(models.Model):
    pass

class FacultiesGrantType(models.Model):
    pass

class Address(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    friendlyName = models.CharField(max_length=255, null=False)
    address1 = models.CharField(max_length=255, null=False)
    address2 = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=False)
    state = models.CharField(max_length=255, null=False)
    zip_code = models.CharField(max_length=10, null=False)
    country = models.CharField(max_length=255, null=False)

    class Meta:
        ordering = ['friendlyName']
        db_table = 'address'
    
    def __str__(self):
        return f"{self.friendlyName}: {self.address1}"

class DioceseOrder(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    is_order = models.BooleanField(null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'diocese_order'
        
    def __str__(self):
        return f"{self.name}"

class EasternChurch(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'eastern_church'
    
    def __str__(self):
        return f"{self.name}"

class Person(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    personType = models.Choices(
        ('priest', 'Priest'),
        ('deacon', 'Deacon'),
        ('lay', 'Lay Person'),
    )
    prefix = models.Choices(
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('mrs', 'Mrs.'),
        ('dr', 'Dr.'),
        ('reverend', 'Reverend'),
        ('very_reverend', 'Very Reverend'),
        ('reverend_monsignor', 'Reverend Monsignor'),
        ('most_reverend', 'Most Reverend'),
    )
    residencyType = models.Choices(
        ('parish_rectory', 'Parish Rectory'),
        ('diocesan_property', 'Diocesan Property'),
        ('diocesan_seminary', 'Diocesan Seminary'),
        ('religious_house', 'Religious House'),
        ('private_residence', 'Private Residence'),
        ('retiirement_community', 'Retirement Community'),
        ('assisted_living', 'Assisted Living'),
        ('nursing_home', 'Nursing Home'),
        ('parish_property', 'Parish Property'),
        ('other', 'Other'),
    )
    activeOutsideDOC = models.Choices(
        ('__blank__', 'Select an option'),
    )
    legalStatus = models.Choices(
        ('naturalBorn_citizen', 'Natural Born U.S. Citizen'),
        ('naturalized_citizen', 'Naturalized U.S. Citizen'),
        ('permanent_resident', 'Legal permanent U.S. resident (Green Card)'),
        ('religious_visa', 'Religious Visa'),
        ('other_visa', 'Other Visa'),
        ('unsure', 'Unsure'),
    )
    name_first = models.CharField(max_length=255, null=False)
    name_middle = models.CharField(max_length=255, null=True)
    name_last = models.CharField(max_length=255, null=False)
    suffix = models.CharField(max_length=255, null=True)
    photo = models.ImageField(upload_to='../media/photos/', null=True) #Needs to move to a perminant file system like mongoDB
    date_birth = models.DateField(null=True)
    date_retired = models.DateField(null=True)
    date_deceased = models.DateField(null=True)
    date_baptism = models.DateField(null=True)
    is_safeEnvironmentTraining = models.BooleanField(null=True)
    lkp_residence_id = models.ForeignKey(Address,
                                        on_delete=models.CASCADE,
                                         ull=True)
    lkp_mailing_id = models.ForeignKey(Address,
                                        on_delete=models.CASCADE,
                                        null=True)
    
    class Meta:
        ordering = ['name_last']
        db_table = 'person'
        
    def __str__(self):
        if self.name_middle and self.suffix:
            return f"{self.name_last}, {self.name_first} {self.name_middle} {self.suffix}"
        elif self.name_middle and not self.suffix:
            return f"{self.name_last}, {self.name_first} {self.name_middle}"
        elif self.suffix and not self.name_middle:
            return f"{self.name_last}, {self.name_first} {self.suffix}"
        elif not self.name_middle and not self.suffix:
            return f"{self.name_last}, {self.name_first}"

class Person_Title(models.Model):
    pass

class Person_FacultiesGrant(models.Model):
    pass

class Person_Relationship(models.Model):
    pass

class Person_DegreeCertificate(models.Model):
    pass

class Person_Phone(models.Model):
    pass

class Person_Email(models.Model):
    pass

class Person_Language(models.Model):
    pass

class Person_Status(models.Model):
    pass

class Vicariate(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    map = models.FileField(upload_to='../media/maps/', null=True)
    lkp_vicarForane_id = models.ForeignKey(Person,
                                        on_delete=models.CASCADE,
                                        null=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'vicariate'
        
    def __str__(self):
        return f"{self.name}"

class County(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'county'
        
    def __str__(self):
        return f"{self.name}"

class Location(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    type = models.Choices(
        ('church', 'Church'),
        ('school', 'School'),
        ('campus_ministry', 'Campus Ministry'),
        ('hospital/hospice', 'Hospital/Hospice'),
        ('other_entity', 'Other Entity'),
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    website = models.URLField(max_length=255, null=True)
    lkp_physicalAddress_id = models.ForeignKey(Address,
                                               on_delete=models.CASCADE,
                                               null=True)
    lkp_mailingAddress_id = models.ForeignKey(Address,
                                               on_delete=models.CASCADE,
                                               null=True)
    lkp_vicariate_id = models.ForeignKey(Vicariate,
                                        on_delete=models.CASCADE,
                                        null=True)
    lkp_county_id = models.ForeignKey(County,
                                        on_delete=models.CASCADE,
                                        null=True)
    
    class Meta:
        ordering = ['name']
        db_table = 'location'
        
    def __str__(self):
        return f"{self.locationName}"

class Location_Status(models.Model):
    pass

class Location_Email(models.Model):
    pass

class Location_Phone(models.Model):
    pass
class Lay_Detail(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'lay'
        
    def __str__(self):
        if self.lkp_person_id.name_middle and self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.name_middle} {self.lkp_person_id.suffix}"
        elif self.lkp_person_id.name_middle and not self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.name_middle}"
        elif self.lkp_person_id.suffix and not self.lkp_person_id.name_middle:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.suffix}"
        elif not self.lkp_person_id.name_middle and not self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first}" 

class Deacon_Detail(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'deacon'
        
    def __str__(self):
        if self.lkp_person_id.name_middle and self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.name_middle} {self.lkp_person_id.suffix}"
        elif self.lkp_person_id.name_middle and not self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.name_middle}"
        elif self.lkp_person_id.suffix and not self.lkp_person_id.name_middle:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.suffix}"
        elif not self.lkp_person_id.name_middle and not self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first}" 

class Priest_Detail(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_dioceseOrder_id = models.ForeignKey(DioceseOrder,
                                        on_delete=models.CASCADE,
                                        null=True)
    lkp_residenceDiocese_id = models.ForeignKey(DioceseOrder,
                                        on_delete=models.CASCADE,
                                        null=True)
    lkp_dioceseOrderOrdination_id = models.ForeignKey(DioceseOrder,
                                        on_delete=models.CASCADE,
                                        null=True)
    lkp_dioceseOrderIncardination_id = models.ForeignKey(DioceseOrder,
                                        on_delete=models.CASCADE,
                                        null=True)
    lkp_easternChurchName_id = models.ForeignKey(EasternChurch,
                                                on_delete=models.CASCADE,
                                                null=True)
    lkp_emergencyContact1_id = models.ForeignKey(Person,
                                        on_delete=models.CASCADE,
                                        null=True)
    lkp_emergencyContact2_id = models.ForeignKey(Person,
                                        on_delete=models.CASCADE,
                                        null=True)
    lkp_placeOfBaptism_id = models.ForeignKey(Location,
                                        on_delete=models.CASCADE,
                                        null=True)
    religiousInstituteType = models.Choices(
        ('__blank__', 'Select an option'),
    )
    religiousOrderProvince = models.Choices(
        ('__blank__', 'Select an option'),
    )
    officialCatholicDirectoryStatus = models.Choices(
        ('__blank__', 'Select an option'),
    )
    religiousSuffix = models.Choices(
        ('__blank__', 'Select an option'),
    )
    diocesanSuffix = models.Choices(
        ('__blank__', 'Select an option'),
    )
    incardinationHistory = models.TextField(null=True)
    diocesanReligious = models.Choices(
        ('religious', 'Religious'),
        ('diocesan', 'Diocesan'),
    )
    is_shareCellPhone = models.BooleanField(null=True)
    is_easternCatholicChurchMember = models.BooleanField(null=True)
    is_massEnglish = models.BooleanField(null=True)
    is_massSpanish = models.BooleanField(null=True)
    is_sacramentsEnglish = models.BooleanField(null=True)
    is_sacramentsSpanish = models.BooleanField(null=True)
    is_incardinationRequested = models.BooleanField(null=True)
    is_incardinationAccepted = models.BooleanField(null=True)
    is_facultiesGranted = models.BooleanField(null=True)
    is_externPriestDurationRenewable = models.BooleanField(null=True)
    is_approvedLetterOfGoodStanding = models.BooleanField(null=True)
    is_includeOfficialCatholicDirectory = models.BooleanField(null=True)
    is_optedOut_ss_medicare = models.BooleanField(null=True)
    is_legalWillComplete = models.BooleanField(null=True)
    is_legalWillChanceryFile = models.BooleanField(null=True)
    is_powerAttorney = models.BooleanField(null=True)
    is_powerAttorneyChanceryFile = models.BooleanField(null=True)
    is_backgroundComplete = models.BooleanField(null=True)
    date_ordination = models.DateField(null=True)
    date_transitionalDiaconateOrdination = models.DateField(null=True)
    date_priestOrdination = models.DateField(null=True)
    date_episcopalOrdination = models.DateField(null=True)
    date_incardination = models.DateField(null=True)
    date_incardinationRequested = models.DateField(null=True)
    date_facultiesRequested = models.DateField(null=True)
    date_facultiesGranted = models.DateField(null=True)
    date_externPriestAssignmentStart = models.DateField(null=True)
    date_externPriestAssignmentEnd = models.DateField(null=True)
    date_onboard = models.DateField(null=True)
    date_baptism = models.DateField(null=True)
    externPriestExpectedDurationMonths = models.IntegerField(null=True)
    priestCode = models.IntegerField(null=True)
    misconduct = models.TextField(null=True)
    birth_city = models.CharField(max_length=255, null=True)
    birth_state = models.CharField(max_length=255, null=True)
    birth_country = models.CharField(max_length=255, null=True)
    notes = models.TextField(null=True)
    otherSkillsCompentencies = models.TextField(null=True)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'priest'
        
    def __str__(self):
        if self.lkp_person_id.name_middle and self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.name_middle} {self.lkp_person_id.suffix}"
        elif self.lkp_person_id.name_middle and not self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.name_middle}"
        elif self.lkp_person_id.suffix and not self.lkp_person_id.name_middle:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} {self.lkp_person_id.suffix}"
        elif not self.lkp_person_id.name_middle and not self.lkp_person_id.suffix:
            return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first}" 
    
class Church_Detail(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    parishUniqueName = models.CharField(max_length=255, null=False)
    boundary = models.FileField(upload_to='../media/boundaries/', null=True)
    is_mission = models.BooleanField(null=False)
    is_doc = models.BooleanField(null=False)
    tax_id = models.CharField(max_length=255, null=True)
    cityServed = models.CharField(max_length=255, null=True)
    geo_id = models.BigIntegerField(null=True)
    parish_id = models.BigIntegerField(null=False)
    type_id = models.BigIntegerField(null=True)
    date_established = models.DateField(null=True)
    date_firstDedication = models.DateField(null=True)
    date_secondDedication = models.DateField(null=True)
    notes = models.TextField(null=True)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'church'
        
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class Church_Language(models.Model):
    pass

class CampusMinistry_Detail(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    is_massAtParish = models.BooleanField(null=False)
    lkp_church_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=True)
    universityServed = models.CharField(max_length=255, null=True)
    sundayMassSchedule = models.TextField(null=True)
    campusMinistryHours = models.TextField(null=True)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'campus_ministry'
    
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class School_Detail(models.Model):
    pass

class Hospital_Detail(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    facilityType = models.Choices(
        ('hospital', 'Hospital'),
        ('hospice', 'Hospice'),
    )
    diocese = models.Choices(
        ('diocese_of_charlotte', 'Diocese of Charlotte'),
        ('diocese_of_raleigh', 'Diocese of Raleigh'),
    )
    lkp_parishBoundary_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=True)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'hospital'
        
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class OtherEntity_Detail(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'other_entity'
        
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class Mission_Connection(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    lkp_mission_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_parish_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    
    class Meta:
        ordering = ['lkp_mission_id__name']
        db_table = 'mission_connections'
        
    def __str__(self):
        return f"{self.lkp_mission_id.name} => {self.lkp_parish_id.name}"