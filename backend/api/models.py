from django.db import models
from django.core.validators import ( 
                                    RegexValidator, 
                                    MinLengthValidator, 
                                    MaxLengthValidator,
                                    MinValueValidator
)

# Create your models here.
class Status(models.Model):
    choice_type = [
        ('priest', 'Priest'),
        ('deacon', 'Deacon'),
        ('lay', 'Lay Person'),
        ('church', 'Church'),
        ('campus_ministry', 'Campus Ministry'),
        ('hospital/hospice', 'Hospital/Hospice'),
        ('school', 'School'),
        ('other_entity', 'Other Entity'),
    ]
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=255, choices=choice_type, null=False)
    class Meta:
        ordering = ['name']
        db_table = 'status'
        
    def __str__(self):
        return f"{self.name}"

class EmailType(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'email_type'
        
    def __str__(self):
        return f"{self.name}"

class PhoneType(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'phone_type'
        
    def __str__(self):
        return f"{self.name}"

class Language(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'language'
    
    def __str__(self):
        return f"{self.name}"

class LanguageProficiency(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'language_proficiency'
        
    def __str__(self):
        return f"{self.name}"

class SubjectMatter(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'subject_matter'
        
    def __str__(self):
        return f"{self.name}"

class TypeOfDegree(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)

    class Meta:
        ordering = ['name']
        db_table = 'type_of_degree'
    
    def __str__(self):
        return f"{self.name}"

class DegreeCertificate(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    institute = models.CharField(max_length=255, null=False)
    lkp_subjectMatter_id = models.ForeignKey(SubjectMatter,
                                        on_delete=models.CASCADE,
                                        null=True)
    lkp_typeOfDegree_id = models.ForeignKey(TypeOfDegree,
                                        on_delete=models.CASCADE,
                                        null=True)
    
    class Meta:
        ordering = ['institute']
        db_table = 'degree_certificate'
        
    def __str__(self):
        return f"{self.institute}: {self.lkp_subjectMatter_id} - {self.lkp_typeOfDegree_id}"

class RelationshipType(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'relationship_type'
        
    def __str__(self):
        return f"{self.name}"

class Title(models.Model):
    choice_personType = [
        ('priest', 'Priest'),
        ('deacon', 'Deacon'),
        ('lay', 'Lay Person'),
        ]
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    personType = models.CharField(max_length=255, choices=choice_personType, null=False)
    is_ecclesiastical = models.BooleanField(null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'title'
        
    def __str__(self):
        return f"{self.name}"

class FacultiesGrantType(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'faculties_grant_type'
        
    def __str__(self):
        return f"{self.name}"

class Address(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
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
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    is_order = models.BooleanField(null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'diocese_order'
        
    def __str__(self):
        return f"{self.name}"

class EasternChurch(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'eastern_church'
    
    def __str__(self):
        return f"{self.name}"

class Person(models.Model):
    choice_personType = [
        ('priest', 'Priest'),
        ('deacon', 'Deacon'),
        ('lay', 'Lay Person'),
    ]
    choice_prefix = [
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('mrs', 'Mrs.'),
        ('dr', 'Dr.'),
        ('reverend', 'Reverend'),
        ('very_reverend', 'Very Reverend'),
        ('reverend_monsignor', 'Reverend Monsignor'),
        ('most_reverend', 'Most Reverend'),
    ]
    choice_residencyType = [
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
    ]
    choice_activeOutsideDOC = [
        ('__blank__', 'Select an option'),
    ]
    choice_legalStatus = [
        ('naturalBorn_citizen', 'Natural Born U.S. Citizen'),
        ('naturalized_citizen', 'Naturalized U.S. Citizen'),
        ('permanent_resident', 'Legal permanent U.S. resident (Green Card)'),
        ('religious_visa', 'Religious Visa'),
        ('other_visa', 'Other Visa'),
        ('unsure', 'Unsure'),
    ]
    
    #id = models.BigIntegerField(primary_key=True, null=False)
    personType = models.CharField(max_length=255, choices=choice_personType, null=False)
    prefix = models.CharField(max_length=255, choices=choice_prefix, null=True)
    residencyType = models.CharField(max_length=255, choices=choice_residencyType, null=True)
    activeOutsideDOC = models.CharField(max_length=255, choices=choice_activeOutsideDOC, null=True)
    legalStatus = models.CharField(max_length=255, choices=choice_legalStatus, null=True)
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
                                        null=True,
                                        related_name='person_residence')
    lkp_mailing_id = models.ForeignKey(Address,
                                        on_delete=models.CASCADE,
                                        null=True,
                                        related_name='person_mailing')
    
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

class Person_FacultiesGrant(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_faultiesGrantType_id = models.ForeignKey(FacultiesGrantType,
                                        on_delete=models.CASCADE,
                                        null=False)
    date_granted = models.DateField(null=False)
    date_modified = models.DateField(null=True)
    date_removed = models.DateField(null=True)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'person_faculties_grant'
        
    def __str__(self):
        return f"{self.lkp_person_id.name_last if self.lkp_person_id else ''}, {self.lkp_person_id.name_first if self.lkp_person_id else ''} - {self.lkp_faultiesGrantType_id.name if self.lkp_faultiesGrantType_id else ''}: {self.date_granted} - {self.date_modified} - {self.date_removed}"

class Person_Relationship(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_relationshipType_id = models.ForeignKey(RelationshipType,
                                        on_delete=models.CASCADE,
                                        null=False)
    lkp_firstPerson_id = models.ForeignKey(Person,
                                        on_delete=models.CASCADE,
                                        null=False,
                                        related_name='first_person')
    lkp_secondPerson_id = models.ForeignKey(Person,
                                        on_delete=models.CASCADE,
                                        null=False,
                                        related_name='second_person')
    
    class Meta:
        ordering = ['lkp_firstPerson_id__name_last']
        db_table = 'person_relationship'
        
    def __str__(self):
        return f"{self.lkp_firstPerson_id.name_last}, {self.lkp_firstPerson_id.name_first} - {self.lkp_relationshipType_id.name}: {self.lkp_secondPerson_id.name_last}, {self.lkp_secondPerson_id.name_first}"

class Person_DegreeCertificate(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_degreeCertificate_id = models.ForeignKey(DegreeCertificate,
                                        on_delete=models.CASCADE,
                                        null=False)
    date_acquired = models.DateField(null=True)
    date_expiration = models.DateField(null=True)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'person_degree_certificate'
    
    def __str__(self):
        return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} - {self.lkp_degreeCertificate_id.institute}: {self.lkp_degreeCertificate_id.lkp_subjectMatter_id} - {self.lkp_degreeCertificate_id.lkp_typeOfDegree_id}"

class Person_Phone(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_phoneType_id = models.ForeignKey(PhoneType,
                                        on_delete=models.CASCADE,
                                        null=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phoneNumber = models.CharField(validators=[phone_regex], max_length=17,blank=True, null=False) # validators should be a list
    is_primary = models.BooleanField(null=False)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'person_phone'
        
    def __str__(self):
        return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} - {self.lkp_phoneType_id.name}: {self.phoneNumber}"

class Person_Email(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_emailType_id = models.ForeignKey(EmailType,
                                        on_delete=models.CASCADE,
                                        null=False)
    email_regex = RegexValidator(regex=r'^[a-zA-Z0-9\.\-_+%]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+$', message="Email must be in a valid format.")
    email = models.EmailField(validators=[email_regex], max_length=255, blank=True, null=False) # validators should be a list
    is_primary = models.BooleanField(null=False)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'person_email'
        
    def __str__(self):
        return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} - {self.lkp_emailType_id.name}: {self.email}"

class Person_Language(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_language_id = models.ForeignKey(Language,
                                        on_delete=models.CASCADE,
                                        null=False)
    lkp_languageProficiency_id = models.ForeignKey(LanguageProficiency,
                                        on_delete=models.CASCADE,
                                        null=False)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'person_language'
        
    def __str__(self):
        return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} - {self.lkp_language_id.name}: {self.lkp_languageProficiency_id.name}"

class Person_Status(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_status_id = models.ForeignKey(Status,
                                        on_delete=models.CASCADE,
                                        null=False)
    date_assigned = models.DateField(null=False)
    date_released = models.DateField(null=True)
    details = models.TextField(null=True)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'person_status'
        
    def __str__(self):
        return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} - {self.lkp_status_id.name}: {self.date_assigned} - {self.date_released}"

class Vicariate(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
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

class Person_Title(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_title_id = models.ForeignKey(Title,
                                    on_delete=models.CASCADE,
                                    null=False)
    date_assigned = models.DateField(null=False)
    date_expiration = models.DateField(null=True)
    # Only used for special titles
    lkp_vicariate_id = models.ForeignKey(Vicariate,
                                        on_delete=models.CASCADE,
                                        null=True)
    
    class Meta:
        ordering = ['lkp_person_id__name_last']
        db_table = 'person_title'
        
    def __str__(self):
        return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} - {self.lkp_title_id.name}: {self.date_assigned} - {self.date_expiration}"

class County(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'county'
        
    def __str__(self):
        return f"{self.name}"

class Location(models.Model):
    choice_type = [
        ('church', 'Church'),
        ('school', 'School'),
        ('campus_ministry', 'Campus Ministry'),
        ('hospital/hospice', 'Hospital/Hospice'),
        ('other_entity', 'Other Entity'),
    ]

    #id = models.BigIntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=255, choices=choice_type, null=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    website = models.URLField(max_length=255, null=True)
    lkp_physicalAddress_id = models.ForeignKey(Address,
                                               on_delete=models.CASCADE,
                                               null=True,
                                               related_name='location_physicalAddress')
    lkp_mailingAddress_id = models.ForeignKey(Address,
                                               on_delete=models.CASCADE,
                                               null=True,
                                               related_name='location_mailingAddress')
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
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_status_id = models.ForeignKey(Status,
                                        on_delete=models.CASCADE,
                                        null=False)
    date_assigned = models.DateField(null=False)
    date_released = models.DateField(null=True)
    details = models.TextField(null=True)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'location_status'
        
    def __str__(self):
        return f"{self.lkp_location_id.name} - {self.lkp_status_id.name}: {self.date_assigned} - {self.date_released}"

class Location_Email(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_emailType_id = models.ForeignKey(EmailType,
                                        on_delete=models.CASCADE,
                                        null=False)
    email_regex = RegexValidator(regex=r'^[a-zA-Z0-9\.\-_+%]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+$', message="Email must be in a valid format.")
    email = models.EmailField(validators=[email_regex], max_length=255, blank=True, null=False) # validators should be a list
    is_primary = models.BooleanField(null=False)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'location_email'
        
    def __str__(self):
        return f"{self.lkp_location_id.name} - {self.lkp_emailType_id.name}: {self.email}"

class Location_Phone(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_phoneType_id = models.ForeignKey(PhoneType,
                                        on_delete=models.CASCADE,
                                        null=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phoneNumber = models.CharField(validators=[phone_regex], max_length=17,blank=True, null=False) # validators should be a list
    is_primary = models.BooleanField(null=False)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'location_phone'
        
    def __str__(self):
        return f"{self.lkp_location_id.name} - {self.lkp_phoneType_id.name}: {self.phoneNumber}"

class Lay_Detail(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
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
        return "Unknown Person"

class Deacon_Detail(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
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
    choice_religiousInstituteType = [
        ('__blank__', 'Select an option'),
    ]
    choice_religiousOrderProvince = [
        ('__blank__', 'Select an option'),
    ]
    choice_officialCatholicDirectoryStatus = [
        ('__blank__', 'Select an option'),
    ]
    choice_religiousSuffix = [
        ('__blank__', 'Select an option'),
    ]
    choice_religiousSuffix = [
        ('__blank__', 'Select an option'),
    ]
    choice_diocesanReligious = [
        ('religious', 'Religious'),
        ('diocesan', 'Diocesan'),
    ]

    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_person_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_dioceseOrder_id = models.ForeignKey(DioceseOrder,
                                        on_delete=models.CASCADE,
                                        null=True,
                                        related_name='priest_dioceseOrder')
    lkp_residenceDiocese_id = models.ForeignKey(DioceseOrder,
                                        on_delete=models.CASCADE,
                                        null=True,
                                        related_name='priest_residenceDiocese')
    lkp_dioceseOrderOrdination_id = models.ForeignKey(DioceseOrder,
                                        on_delete=models.CASCADE,
                                        null=True,
                                        related_name='priest_dioceseOrderOrdination')
    lkp_dioceseOrderIncardination_id = models.ForeignKey(DioceseOrder,
                                        on_delete=models.CASCADE,
                                        null=True,
                                        related_name='priest_dioceseOrderIncardination')
    lkp_easternChurch_id = models.ForeignKey(EasternChurch,
                                                on_delete=models.CASCADE,
                                                null=True)
    """ Moved this to relationships so its no longer needed here."""
    # lkp_emergencyContact1_id = models.ForeignKey(Person,
    #                                     on_delete=models.CASCADE,
    #                                     null=True)
    # lkp_emergencyContact2_id = models.ForeignKey(Person,
    #                                     on_delete=models.CASCADE,
    #                                     null=True)
    lkp_placeOfBaptism_id = models.ForeignKey(Location,
                                        on_delete=models.CASCADE,
                                        null=True)
    religiousInstituteType = models.CharField(max_length=255, choices=choice_religiousInstituteType, null=True)
    religiousOrderProvince = models.CharField(max_length=255, choices=choice_religiousOrderProvince, null=True)
    officialCatholicDirectoryStatus = models.CharField(max_length=255, choices=choice_officialCatholicDirectoryStatus, null=True)
    religiousSuffix = models.CharField(max_length=255, choices=choice_religiousSuffix, null=True)
    diocesanSuffix = models.CharField(max_length=255, choices=choice_religiousSuffix, null=True)
    incardinationHistory = models.TextField(null=True)
    diocesanReligious = models.CharField(max_length=255, choices=choice_diocesanReligious, null=True)
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
        db_table = 'priestDetail'
        
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
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False,
                                    related_name='churchDetail_location')
    lkp_missionOf_id = models.ForeignKey(Location,
                                      on_delete=models.CASCADE,
                                      null=True,
                                      limit_choices_to={'church_detail__lkp_location_id__isnull': False},
                                      related_name='churchDetail_mission')
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
        db_table = 'churchDetail'
        
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class Church_Language(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_church_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    lkp_language_id = models.ForeignKey(Language,
                                        on_delete=models.CASCADE,
                                        null=False)
    massTime = models.TimeField(null=False)
    
    class Meta:
        ordering = ['lkp_church_id__name']
        db_table = 'church_language'
        
    def __str__(self):
        return f"{self.lkp_church_id.name} - {self.lkp_language_id.name}: {self.massTime}"

class CampusMinistry_Detail(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False,
                                    related_name='campusMinistry_location')
    is_massAtParish = models.BooleanField(null=False)
    lkp_church_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    limit_choices_to={'church_detail__lkp_location_id__isnull': False},
                                    related_name='campusMinistry_church')
    universityServed = models.CharField(max_length=255, null=True)
    sundayMassSchedule = models.TextField(null=True)
    campusMinistryHours = models.TextField(null=True)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'campusMinistryDetail'
    
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class Hospital_Detail(models.Model):
    choice_diocese = [
        ('diocese_of_charlotte', 'Diocese of Charlotte'),
        ('diocese_of_raleigh', 'Diocese of Raleigh'),
    ]
    choice_facilityType = [
        ('hospital', 'Hospital'),
        ('hospice', 'Hospice'),
    ]

    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False,
                                    related_name='hospital_location')
    facilityType = models.CharField(max_length=255, choices=choice_facilityType, null=False)
    diocese = models.CharField(max_length=255, choices=choice_diocese, null=False)
    lkp_parishBoundary_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='hospital_boundary')
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'hospitalDetail'
        
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class OtherEntity_Detail(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False)
    
    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'otherEntityDetail'
        
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class MissionConnection(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_mission_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False,
                                    related_name='mission')
    lkp_parish_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False,
                                    related_name='parish')
    
    class Meta:
        ordering = ['lkp_mission_id__name']
        db_table = 'mission_connections'
        
    def __str__(self):
        return f"{self.lkp_mission_id.name} => {self.lkp_parish_id.name}"

class SchoolDetail(models.Model):
    choices_schoolType = [
        ('elementary', 'Elementary'),
        ('middle', 'Middle School'),
        ('secondary', 'Secondary'),
    ]
    choices_gradeLevels = [
        ('tk-5', 'TK - 5th'),
        ('pk-5', 'PK - 5th'),
        ('pk-8', 'PK - 8th'),
        ('k-5', 'K - 5th'),
        ('k-8', 'K - 8th'),
        ('6-8', '6th - 8th'),
        ('9-12', '9th - 12th'),
    ]
    choices_locationType = [
        ('innercity', 'Inner City'),
        ('rural', 'Rural'),
        ('suburban', 'Suburban'),
        ('urban', 'Urban'), 
    ]
    choices_sponsorship = [
        ('diocesan', 'Diocesan'),
        ('inter-parish', 'Inter-Parish'),
        ('parish', 'Parish'),
    ]
    choice_schoolGender = [
        ('co-ed', 'Co-Ed'),   
    ]
    
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_location_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=False,
                                    related_name='school_location')
    schoolCode = models.BigIntegerField(null=False)
    schoolType = models.CharField(max_length=255, choices=choices_schoolType, null=False)
    gradeLevels = models.CharField(max_length=255, choices=choices_gradeLevels, null=False)
    lkp_affiliatedParishParish_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    limit_choices_to={'church_detail__lkp_location_id__isnull': False},
                                    related_name='school_affiliatedParish')
    lkp_parishProperty_id = models.ForeignKey(Location,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    limit_choices_to={'church_detail__lkp_location_id__isnull': False},
                                    related_name='school_parishProperty')
    lkp_president_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_president') 
    lkp_principal_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_principal')
    lkp_vicePrincipal_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_vicePrincipal')
    lkp_campusMinister_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_campusMinister')
    lkp_assistantPrincipal1_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_assistantPrincipal1')
    lkp_assistantPrincipal2_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_assistantPrincipal2')
    lkp_assistantPrinciapl3_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_assistantPrincipal3')
    lkp_deanOfStudents1_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_deanOfStudents1')
    lkp_deanOfStudents2_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='school_deanOfStudents2')
    locationType = models.CharField(max_length=255, choices=choices_locationType, null=False)
    sponsorship = models.CharField(max_length=255, choices=choices_sponsorship, null=False)
    schoolGender = models.CharField(max_length=255, choices=choice_schoolGender, null=False)
    is_MACS = models.BooleanField(null=False)
    highSchoolReligiousEd = models.BigIntegerField(null=True)
    prek_8religiousEd = models.BigIntegerField(null=True)
    lkp_chaplain_id = models.ForeignKey(Person,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    limit_choices_to={'priest_detail__lkp_person_id__isnull': False},
                                    related_name='school_chaplain')
    academicPriest = models.BigIntegerField(null=True)
    academicBrother = models.BigIntegerField(null=True)
    academicSister = models.BigIntegerField(null=True)
    academicLay = models.BigIntegerField(null=True)
    canonicalStatus = models.CharField(max_length=255, null=True)
    is_schoolChapel = models.BooleanField(null=True)

    class Meta:
        ordering = ['lkp_location_id__name']
        db_table = 'school'
        
    def __str__(self):
        return f"{self.lkp_location_id.name}"

class Enrollment(models.Model):
    choice_year = [
        ('2023-2024', '2023 - 2024'),
        ('2024-2025', '2024 - 2025'),
        ('2024-2025', '2024 - 2025'),
        ('2025-2026', '2025 - 2026'),
    ]
    
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_school_id = models.ForeignKey(Location,
                                      on_delete=models.CASCADE,
                                      limit_choices_to={'school_detail__lkp_location_id__isnull': False},
                                      null=False)
    year = models.CharField(max_length=255,choices=choice_year, null=False)
    prek = models.BigIntegerField(null=True)
    transitionalKindergarden = models.BigIntegerField(null=True)
    kindergarden = models.BigIntegerField(null=True)
    grade_1 = models.BigIntegerField(null=True)
    grade_2 = models.BigIntegerField(null=True)
    grade_3 = models.BigIntegerField(null=True)
    grade_4 = models.BigIntegerField(null=True)
    grade_5 = models.BigIntegerField(null=True)
    grade_6 = models.BigIntegerField(null=True)
    grade_7 = models.BigIntegerField(null=True)
    grade_8 = models.BigIntegerField(null=True)
    grade_9 = models.BigIntegerField(null=True)
    grade_10 = models.BigIntegerField(null=True)
    grade_11 = models.BigIntegerField(null=True)
    grade_12 = models.BigIntegerField(null=True)

    class Meta:
        ordering = ['lkp_school_id__name']
        db_table = 'enrollment'
    
    def __str__(self):
        return f'{self.lkp_school_id.name} - {self.year}'

class AssignmentType(models.Model):
    choice_personType = [
        ('deacon', 'Deacon'),
        ('priest', 'Priest'),
        ('lay', 'Lay')
    ]   
    #id = models.BigIntegerField(primary_key=True, null=False)
    title = models.CharField(max_length=255, null=False)
    personType = models.CharField(max_length=255, choices=choice_personType, null=False)
    class Meta:
        ordering = ['title']
        db_table = 'assignmentType'
    def __str__(self):
        return f'{self.title}'

class Assignment(models.Model):
    #id = models.BigIntegerField(primary_key=True, null=False)
    lkp_assignmentType_id = models.ForeignKey(AssignmentType,
                                              on_delete=models.CASCADE,
                                              null=False)
    lkp_location_id = models.ForeignKey(Location,
                                        on_delete=models.CASCADE,
                                        null=False)
    lkp_person_id = models.ForeignKey(Person,
                                      on_delete=models.CASCADE,
                                      null=False)
    date_assigned = models.DateField(null=False)
    date_released = models.DateField(null=True)
    term = models.BigIntegerField(null=False)
    
    class Meta:
        ordering = ['lkp_assignmentType_id__title']
        db_table = 'assignment'

    def __str__(self):
        return f'{self.lkp_assignmentType_id.name}:{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} at {self.lkp_location_id.name}'

class StatusAnimarum(models.Model):
    choice_year = [
        ('2020-21', '2020-21'),
        ('2023-24', '2023-24'),
        ('2024-25', '2024-25')
    ]
    choice_schoolType = [
        ('inter-parochial', 'Inter-Parochial'),
        ('macs', 'MACS'),
        ('parochial', 'Parochial')
    ]
    
    lkp_church_id = models.ForeignKey(Location,
                                      on_delete=models.CASCADE,
                                      null=False,
                                      limit_choices_to={'church_detail__lkp_location_id__isnull': False},
                                      related_name='statusAnimarum_church')
    year = models.CharField(default=choice_year[-1],choices=choice_year, null=False)
    percentFullTime_deacons = models.DecimalField(max_digits = 5, 
                                                  decimal_places =2 , 
                                                  default = 0.0, 
                                                  null = False,
                                                  validators = [
                                                      MinLengthValidator(0.0),
                                                      MaxLengthValidator(100.0)
                                                  ])
    percentFullTime_brothers = models.DecimalField(max_digits = 5,
                                                   decimal_places = 2,
                                                   default = 0.0,
                                                   null = False,
                                                   validators = [
                                                       MinLengthValidator(0.0),
                                                       MaxLengthValidator(100.0)
                                                   ])
    percentFullTime_sisters = models.DecimalField(max_digits = 5,
                                                   decimal_places = 2,
                                                   default = 0.0,
                                                   null = False,
                                                   validators = [
                                                       MinLengthValidator(0.0),
                                                       MaxLengthValidator(100.0)
                                                   ]) 
    percentFullTime_other = models.DecimalField(max_digits = 5,
                                                   decimal_places = 2,
                                                   default = 0.0,
                                                   null = False,
                                                   validators = [
                                                       MinLengthValidator(0.0),
                                                       MaxLengthValidator(100.0)
                                                   ])
    percentPartTime_staff = models.DecimalField(max_digits = 5,
                                                   decimal_places = 2,
                                                   default = 0.0,
                                                   null = False,
                                                   validators = [
                                                       MinLengthValidator(0.0),
                                                       MaxLengthValidator(100.0)
                                                   ])
    percent_volunteers = models.DecimalField(max_digits = 5,
                                                   decimal_places = 2,
                                                   default = 0.0,
                                                   null = False,
                                                   validators = [
                                                       MinLengthValidator(0.0),
                                                       MaxLengthValidator(100.0)
                                                   ])
    registeredHouseholds = models.BigIntegerField(default=0, 
                                                    null=False, 
                                                    validators=[
                                                        MinLengthValidator(0)
                                                        ])
    maxMass = models.BigIntegerField(default=0, 
                                    null=False, 
                                    validators=[
                                        MinLengthValidator(0)
                                        ])
    seatingCapacity = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    baptismAge_1_7 = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    baptismAge_8_17 = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    baptismAge_18 = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    fullCommunionRCIA = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    firstCommunion = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    confirmation = models.BigIntegerField(default=0, 
                                        null=False, 
                                        validators=[
                                            MinLengthValidator(0)
                                            ])
    marriage_catholic = models.BigIntegerField(default=0, 
                                                null=False, 
                                                validators=[
                                                    MinLengthValidator(0)
                                                    ])
    marriage_interfaith = models.BigIntegerField(default=0, 
                                                null=False, 
                                                validators=[
                                                    MinLengthValidator(0)
                                                    ])
    deaths = models.BigIntegerField(default=0, 
                                    null=False, 
                                    validators=[
                                        MinLengthValidator(0)
                                        ])
    childrenInFaithFormation = models.BigIntegerField(default=0, 
                                                    null=False, 
                                                    validators=[
                                                        MinLengthValidator(0)
                                                        ])
    school_prek_5 = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    school_grade6_8 = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    school_grade9_12 = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    youthMinistry = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    adult_education = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    adult_sacramentPrep = models.BigIntegerField(default=0, 
                                                null=False, 
                                                validators=[
                                                    MinLengthValidator(0)
                                                    ])
    catechist_paid = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    catechist_vol = models.BigIntegerField(default=0, 
                                            null=False, 
                                            validators=[
                                                MinLengthValidator(0)
                                                ])
    rcia_rcic = models.BigIntegerField(default=0, 
                                        null=False, 
                                        validators=[
                                            MinLengthValidator(0)
                                            ])
    volunteersWorkingYouth = models.BigIntegerField(default=0, 
                                                    null=False, 
                                                    validators=[
                                                        MinLengthValidator(0)
                                                        ])
    percent_african = models.DecimalField(max_digits = 5,
                                        decimal_places = 2,
                                        default = 0.0,
                                        null = False,
                                        validators = [
                                            MinLengthValidator(0.0),
                                            MaxLengthValidator(100.0)
                                        ])
    percent_africanAmerican = models.DecimalField(max_digits = 5,
                                                   decimal_places = 2,
                                                   default = 0.0,
                                                   null = False,
                                                   validators = [
                                                       MinLengthValidator(0.0),
                                                       MaxLengthValidator(100.0)
                                                   ])
    percent_asian = models.DecimalField(max_digits = 5,
                                        decimal_places = 2,
                                        default = 0.0,
                                        null = False,
                                        validators = [
                                            MinLengthValidator(0.0),
                                            MaxLengthValidator(100.0)
                                        ])
    percent_hispanic = models.DecimalField(max_digits = 5,
                                            decimal_places = 2,
                                            default = 0.0,
                                            null = False,
                                            validators = [
                                                MinLengthValidator(0.0),
                                                MaxLengthValidator(100.0)
                                            ])
    percent_americanIndian = models.DecimalField(max_digits = 5,
                                                decimal_places = 2,
                                                default = 0.0,
                                                null = False,
                                                validators = [
                                                    MinLengthValidator(0.0),
                                                    MaxLengthValidator(100.0)
                                                ])
    percent_other = models.DecimalField(max_digits = 5,
                                        decimal_places = 2,
                                        default = 0.0,
                                        null = False,
                                        validators = [
                                            MinLengthValidator(0.0),
                                            MaxLengthValidator(100.0)
                                        ])
    is_censusEstimate = models.BooleanField(default=False, null=False)
    referrals_catholicCharities = models.BigIntegerField(null = True, 
                                                         validators = [
                                                             MinLengthValidator(0)
                                                         ])
    has_homeschoolProgram = models.BooleanField(default=False, null=False)
    has_chileCareDayCare = models.BooleanField(default=False, null=False)
    has_scoutingProgram = models.BooleanField(default=False, null=False)
    has_chapelOnCampus = models.BooleanField(default=False, null=False)
    has_adorationChapelOnCampus = models.BooleanField(default=False, null=False)
    has_columbarium = models.BooleanField(default=False, null=False)
    has_cemetary = models.BooleanField(default=False, null=False)
    has_schoolOnSite = models.BooleanField(default=False, null=False)
    schoolType = models.CharField(choices=choice_schoolType, null=True)
    is_nonParochialSchoolUsingFacilities = models.BooleanField(default=False, null=False)
    
    class Meta:
        ordering = ['year', 'lkp_church_id__name']
        db_table = 'statusAnimarum'
    
    def __str__(self):
        return f'{self.year}: {self.lkp_church_id.name}'

class OctoberMassCount(models.Model):
    lkp_church_id = models.ForeignKey(Location,
                                      on_delete=models.CASCADE,
                                      null=False,
                                      limit_choices_to={'church_detail__lkp_location_id__isnull': False},
                                      related_name='octoberCount_church')
    year = models.PositiveIntegerField(null = False, 
                                       validators = [
                                           MinLengthValidator(4), 
                                           MaxLengthValidator(4),
                                            MinValueValidator(2000)
                                           ])
    week1 = models.BigIntegerField(default=0, 
                                   null=False, 
                                   validators= [
                                       MinLengthValidator(0)
                                   ])
    week2 = models.BigIntegerField(default=0, 
                                   null=False, 
                                   validators= [
                                       MinLengthValidator(0)
                                   ])
    week3 = models.BigIntegerField(default=0, 
                                   null=False, 
                                   validators= [
                                       MinLengthValidator(0)
                                   ])
    week4 = models.BigIntegerField(default=0, 
                                   null=False, 
                                   validators= [
                                       MinLengthValidator(0)
                                   ])
    
    class Meta:
        ordering = ['year', 'lkp_church_id__name']
        db_table = 'octoberMassCount'
        
    def __str__(self):
        return f'{self.year}: {self.lkp_church_id.name}'
    
class BuildingOnSite(models.Model):
    name = models.CharField(null=False)
    #Only do this if no other fields required in many to many relationship
    statusAnimarum = models.ManyToManyField(StatusAnimarum,
                                            related_name='statusAnimarum')
    class Meta:
        ordering = ['name']
        db_table = 'buildingsOnSite'
    def __str__(self):
        return f'{self.name}'

class SocialOutreachProgram(models.Model):
    name = models.CharField(null=False)
    #Only do this if no other fields required in many to many relationship
    StatusAnimarum = models.ManyToManyField(StatusAnimarum,
                                            related_name='statusAnimarum')
    
    class Meta:
        ordering = ['name']
        db_table = 'socialOutreachProgram'
        
    def __str__(self):
        return f'{self.name}'
