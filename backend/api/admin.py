from django.contrib import admin
from .models import (
    Address, DioceseOrder, EasternChurch, Language, LanguageProficiency,
    PhoneType, EmailType, RelationshipType, Status, SubjectMatter,
    TypeOfDegree, DegreeCertificate, Vicariate, County, AssignmentType,

    Person,
    Person_FacultiesGrant,
    Person_Relationship,
    Person_DegreeCertificate,
    Person_Phone,
    Person_Email,
    Person_Language,
    Person_Status,
    Person_Title,
    Lay_Detail,
    Deacon_Detail,
    Priest_Detail,

    Location,
    Location_Status,
    Location_Email,
    Location_Phone,
    Church_Detail,
    Church_Language,
    CampusMinistry_Detail,
    Hospital_Detail,
    OtherEntity_Detail,
    MissionConnection,
    SchoolDetail,
    Enrollment,
    Assignment,
    StatusAnimarum,
    OctoberMassCount,
    BuildingOnSite,
    SocialOutreachProgram,
    FilterOption,
)


# ─────────────────────────────────────────────────────────────────────────────
# INLINE CLASSES FOR "PERSON" RELATED TABLES
# ─────────────────────────────────────────────────────────────────────────────
class LayDetailInline(admin.StackedInline):
    model = Lay_Detail
    fk_name = "lkp_person_id"
    can_delete = False
    extra = 0
    verbose_name = "Lay Detail"
    verbose_name_plural = "Lay Details"
    # No additional fields beyond the FK, so we don't need to specify `fields` here.


class DeaconDetailInline(admin.StackedInline):
    model = Deacon_Detail
    fk_name = "lkp_person_id"
    can_delete = False
    extra = 0
    verbose_name = "Deacon Detail"
    verbose_name_plural = "Deacon Details"


class PriestDetailInline(admin.StackedInline):
    model = Priest_Detail
    fk_name = "lkp_person_id"
    can_delete = False
    extra = 0
    verbose_name = "Priest Detail"
    verbose_name_plural = "Priest Details"
    # If you want to limit which fields show up, you can add a `fields = (...)` tuple here.
    # By default, all fields from Priest_Detail will be editable inline.

class PersonPhoneInline(admin.TabularInline):
    model = Person_Phone
    extra = 1
    fields = ("lkp_phoneType_id", "phoneNumber", "is_primary")
    verbose_name = "Phone"
    verbose_name_plural = "Phones"


class PersonEmailInline(admin.TabularInline):
    model = Person_Email
    extra = 1
    fields = ("lkp_emailType_id", "email", "is_primary")
    verbose_name = "Email"
    verbose_name_plural = "Emails"


class PersonLanguageInline(admin.TabularInline):
    model = Person_Language
    extra = 1
    fields = ("lkp_language_id", "lkp_languageProficiency_id")
    verbose_name = "Language"
    verbose_name_plural = "Languages"


class PersonStatusInline(admin.TabularInline):
    model = Person_Status
    extra = 1
    fields = ("lkp_status_id", "date_assigned", "date_released", "details")
    verbose_name = "Status"
    verbose_name_plural = "Statuses"


class PersonFacultiesGrantInline(admin.TabularInline):
    model = Person_FacultiesGrant
    extra = 1
    fields = ("lkp_faultiesGrantType_id", "date_granted", "date_modified", "date_removed")
    verbose_name = "Faculty Grant"
    verbose_name_plural = "Faculty Grants"


class PersonDegreeCertificateInline(admin.TabularInline):
    model = Person_DegreeCertificate
    extra = 1
    fields = ("lkp_degreeCertificate_id", "date_acquired", "date_expiration")
    verbose_name = "Degree/Certificate"
    verbose_name_plural = "Degrees & Certificates"


class PersonTitleInline(admin.TabularInline):
    model = Person_Title
    extra = 1
    fields = ("lkp_title_id", "lkp_vicariate_id", "date_assigned", "date_expiration")
    verbose_name = "Title"
    verbose_name_plural = "Titles"


class PersonRelationshipInline(admin.TabularInline):
    model = Person_Relationship
    extra = 1
    fk_name = "lkp_firstPerson_id"                   # ← must specify which FK points to Person
    fields = ("lkp_relationshipType_id", "lkp_secondPerson_id")
    verbose_name = "Relationship"
    verbose_name_plural = "Relationships"


class AssignmentInlineForPerson(admin.TabularInline):
    model = Assignment
    fk_name = "lkp_person_id"
    extra = 1
    fields = ("lkp_assignmentType_id", "lkp_location_id", "date_assigned", "date_released", "term")
    verbose_name = "Assignment"
    verbose_name_plural = "Assignments"


# ─────────────────────────────────────────────────────────────────────────────
# PERSON ADMIN REGISTRATION
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "personType", "name_last", "name_first", "date_birth")
    search_fields = ("name_first", "name_last")
    list_filter = ("personType",)
    ordering = ("name_last",)

    inlines = [
        LayDetailInline,
        DeaconDetailInline,
        PriestDetailInline,
        PersonPhoneInline,
        PersonEmailInline,
        PersonLanguageInline,
        PersonStatusInline,
        PersonFacultiesGrantInline,
        PersonDegreeCertificateInline,
        PersonTitleInline,
        PersonRelationshipInline,
        AssignmentInlineForPerson,
    ]


# ─────────────────────────────────────────────────────────────────────────────
# INLINE CLASSES FOR "LOCATION" RELATED TABLES
# ─────────────────────────────────────────────────────────────────────────────

class LocationPhoneInline(admin.TabularInline):
    model = Location_Phone
    extra = 1
    fields = ("lkp_phoneType_id", "phoneNumber", "is_primary")
    verbose_name = "Phone"
    verbose_name_plural = "Phones"


class LocationEmailInline(admin.TabularInline):
    model = Location_Email
    extra = 1
    fields = ("lkp_emailType_id", "email", "is_primary")
    verbose_name = "Email"
    verbose_name_plural = "Emails"


class LocationStatusInline(admin.TabularInline):
    model = Location_Status
    extra = 1
    fields = ("lkp_status_id", "date_assigned", "date_released", "details")
    verbose_name = "Status"
    verbose_name_plural = "Statuses"


class ChurchDetailInline(admin.StackedInline):
    model = Church_Detail
    can_delete = False
    fk_name = "lkp_location_id"
    extra = 0
    verbose_name = "Church Detail"
    verbose_name_plural = "Church Details"
    fields = (
        "parishUniqueName", "lkp_missionOf_id", "boundary",
        "is_mission", "is_doc", "tax_id", "cityServed",
        "geo_id", "parish_id", "type_id", "date_established",
        "date_firstDedication", "date_secondDedication", "notes",
    )


class ChurchLanguageInline(admin.TabularInline):
    model = Church_Language
    extra = 1
    fk_name = "lkp_church_id"
    fields = ("lkp_language_id", "massTime")
    verbose_name = "Mass Language"
    verbose_name_plural = "Mass Languages"


class CampusMinistryDetailInline(admin.StackedInline):
    model = CampusMinistry_Detail
    can_delete = False
    fk_name = "lkp_location_id"
    extra = 0
    verbose_name = "Campus Ministry Detail"
    verbose_name_plural = "Campus Ministry Details"
    fields = ("is_massAtParish", "lkp_church_id", "universityServed", "sundayMassSchedule", "campusMinistryHours")


class HospitalDetailInline(admin.StackedInline):
    model = Hospital_Detail
    can_delete = False
    fk_name = "lkp_location_id"
    extra = 0
    verbose_name = "Hospital/Hospice Detail"
    verbose_name_plural = "Hospital/Hospice Details"
    fields = ("facilityType", "diocese", "lkp_parishBoundary_id")


class OtherEntityDetailInline(admin.StackedInline):
    model = OtherEntity_Detail
    can_delete = False
    fk_name = "lkp_location_id"
    extra = 0
    verbose_name = "Other Entity Detail"
    verbose_name_plural = "Other Entity Details"


class MissionConnectionInline(admin.TabularInline):
    model = MissionConnection
    extra = 1
    fk_name = "lkp_parish_id"                      # ← must specify which FK points to Location
    fields = ("lkp_mission_id", "lkp_parish_id")
    verbose_name = "Mission Connection"
    verbose_name_plural = "Mission Connections"


class SchoolDetailInline(admin.StackedInline):
    model = SchoolDetail
    can_delete = False
    fk_name = "lkp_location_id"
    extra = 0
    verbose_name = "School Detail"
    verbose_name_plural = "School Details"
    fields = [
        "schoolCode", "schoolType", "gradeLevels", "lkp_affiliatedParishParish_id",
        "lkp_parishProperty_id", "lkp_president_id", "lkp_principal_id",
        "lkp_vicePrincipal_id", "lkp_campusMinister_id", "lkp_assistantPrincipal1_id",
        "lkp_assistantPrincipal2_id", "lkp_assistantPrinciapl3_id", "lkp_deanOfStudents1_id",
        "lkp_deanOfStudents2_id", "locationType", "sponsorship", "schoolGender",
        "is_MACS", "highSchoolReligiousEd", "prek_8religiousEd", "lkp_chaplain_id",
        "academicPriest", "academicBrother", "academicSister", "academicLay",
        "canonicalStatus", "is_schoolChapel",
    ]


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    fk_name = "lkp_school_id"
    fields = (
        "year", "prek", "transitionalKindergarden", "kindergarden", "grade_1", "grade_2",
        "grade_3", "grade_4", "grade_5", "grade_6", "grade_7", "grade_8",
        "grade_9", "grade_10", "grade_11", "grade_12",
    )
    verbose_name = "Enrollment Record"
    verbose_name_plural = "Enrollment Records"


class AssignmentInlineForLocation(admin.TabularInline):
    model = Assignment
    fk_name = "lkp_location_id"
    extra = 1
    fields = ("lkp_assignmentType_id", "lkp_person_id", "date_assigned", "date_released", "term")
    verbose_name = "Assignment"
    verbose_name_plural = "Assignments"


class StatusAnimarumInline(admin.TabularInline):
    model = StatusAnimarum
    fk_name = "lkp_church_id"
    extra = 1
    fields = (
        "year", "fullTime_deacons", "fullTime_brothers", "fullTime_sisters", "fullTime_other",
        "partTime_staff", "volunteers", "registeredHouseholds", "maxMass", "seatingCapacity",
        "baptismAge_1_7", "baptismAge_8_17", "baptismAge_18", "fullCommunionRCIA", "firstCommunion",
        "confirmation", "marriage_catholic", "marriage_interfaith", "deaths", "childrenInFaithFormation",
        "school_prek_5", "school_grade6_8", "school_grade9_12", "youthMinistry", "adult_education",
        "adult_sacramentPrep", "catechist_paid", "catechist_vol", "rcia_rcic", "volunteersWorkingYouth",
        "percent_african", "percent_africanAmerican", "percent_asian", "percent_hispanic",
        "percent_americanIndian", "percent_other", "is_censusEstimate", "referrals_catholicCharities",
        "has_homeschoolProgram", "has_chileCareDayCare", "has_scoutingProgram", "has_chapelOnCampus",
        "has_adorationChapelOnCampus", "has_columbarium", "has_cemetary", "has_schoolOnSite",
        "schoolType", "is_nonParochialSchoolUsingFacilities",
    )
    verbose_name = "Status Animarum"
    verbose_name_plural = "Status Animarum Records"


class OctoberMassCountInline(admin.TabularInline):
    model = OctoberMassCount
    fk_name = "lkp_church_id"
    extra = 1
    fields = ("year", "week1", "week2", "week3", "week4")
    verbose_name = "October Mass Count"
    verbose_name_plural = "October Mass Counts"


# ─────────────────────────────────────────────────────────────────────────────
# LOCATION ADMIN REGISTRATION
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "lkp_county_id", "lkp_vicariate_id")
    search_fields = ("name",)
    list_filter = ("type",)
    ordering = ("name",)

    inlines = [
        LocationPhoneInline,
        LocationEmailInline,
        LocationStatusInline,
        ChurchDetailInline,
        ChurchLanguageInline,
        CampusMinistryDetailInline,
        HospitalDetailInline,
        OtherEntityDetailInline,
        MissionConnectionInline,
        SchoolDetailInline,
        EnrollmentInline,
        AssignmentInlineForLocation,
        StatusAnimarumInline,
        OctoberMassCountInline,
        # (Removed BuildingOnSiteInline and SocialOutreachProgramInline here,
        #  since those through‐tables do not FK directly to Location.)
    ]


# ─────────────────────────────────────────────────────────────────────────────
# REGISTER “UNRELATED” LOOKUP MODELS SO YOU CAN CREATE/EDIT THEM TOO
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("friendlyName", "address1", "city", "state", "zip_code", "country")
    search_fields = ("friendlyName", "city", "state", "zip_code")
    ordering = ("friendlyName",)


@admin.register(DioceseOrder)
class DioceseOrderAdmin(admin.ModelAdmin):
    list_display = ("name", "is_order")
    search_fields = ("name",)
    list_filter = ("is_order",)
    ordering = ("name",)


@admin.register(EasternChurch)
class EasternChurchAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(LanguageProficiency)
class LanguageProficiencyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(PhoneType)
class PhoneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(EmailType)
class EmailTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(RelationshipType)
class RelationshipTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    search_fields = ("name", "type")
    list_filter = ("type",)
    ordering = ("name",)


@admin.register(SubjectMatter)
class SubjectMatterAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(TypeOfDegree)
class TypeOfDegreeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(DegreeCertificate)
class DegreeCertificateAdmin(admin.ModelAdmin):
    list_display = ("institute", "lkp_subjectMatter_id", "lkp_typeOfDegree_id")
    search_fields = ("institute",)
    list_filter = ("lkp_subjectMatter_id", "lkp_typeOfDegree_id")
    ordering = ("institute",)


@admin.register(Vicariate)
class VicariateAdmin(admin.ModelAdmin):
    list_display = ("name", "lkp_vicarForane_id")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(AssignmentType)
class AssignmentTypeAdmin(admin.ModelAdmin):
    list_display = ("title", "personType")
    search_fields = ("title",)
    list_filter = ("personType",)
    ordering = ("title",)


@admin.register(BuildingOnSite)
class BuildingOnSiteAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("statusAnimarum",)


@admin.register(SocialOutreachProgram)
class SocialOutreachProgramAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("StatusAnimarum",)


@admin.register(FilterOption)
class FilterOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("persons", "locations",)
