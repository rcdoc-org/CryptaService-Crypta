from django.db import models
from djgango.core.validators import RegexValidator

# Create your models here.
class Status(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    type = models.Choices(
        ('priest', 'Priest'),
        ('deacon', 'Deacon'),
        ('lay', 'Lay Person'),
        ('church', 'Church'),
        ('campus_ministry', 'Campus Ministry'),
        ('hospital/hospice', 'Hospital/Hospice'),
        ('school', 'School'),
        ('other_entity', 'Other Entity'),
    )
    
    class Meta:
        ordering = ['name']
        db_table = 'status'
        
    def __str__(self):
        return f"{self.name}"

class EmailType(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'email_type'
        
    def __str__(self):
        return f"{self.name}"

class PhoneType(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'phone_type'
        
    def __str__(self):
        return f"{self.name}"

class Language(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'language'
    
    def __str__(self):
        return f"{self.name}"

class LanguageProficiency(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'language_proficiency'
        
    def __str__(self):
        return f"{self.name}"

class SubjectMatter(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'subject_matter'
        
    def __str__(self):
        return f"{self.name}"

class TypeOfDegree(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)

    class Meta:
        ordering = ['name']
        db_table = 'type_of_degree'
    
    def __str__(self):
        return f"{self.name}"

class DegreeCertificate(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'relationship_type'
        
    def __str__(self):
        return f"{self.name}"

class Title(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    personType = models.Choices(
        ('priest', 'Priest'),
        ('deacon', 'Deacon'),
        ('lay', 'Lay Person'),
    )
    is_ecclesiastical = models.BooleanField(null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'title'
        
    def __str__(self):
        return f"{self.name}"

class FacultiesGrantType(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
    name = models.CharField(max_length=255, null=False)
    
    class Meta:
        ordering = ['name']
        db_table = 'faculties_grant_type'
        
    def __str__(self):
        return f"{self.name}"

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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
        return f"{lkp_person_id.name_last}, {self.lkp_person_id.name_first} - {self.lkp_title_id.name}: {self.date_assigned} - {self.date_expiration}"

class Person_FacultiesGrant(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
        return f"{self.lkp_person_id.name_last}, {self.lkp_person_id.name_first} - {self.lkp_faultiesGrantType_id.name}: {self.date_granted} - {self.date_modified} - {self.date_removed}"

class Person_Relationship(models.Model):
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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
    id = models.BigIntegerField(primary_key=True, increment=True, null=False)
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