"""Models.py is used for managing my user authentication database using
the Django ORM system. We create and modify models to interact with the tables,
of SQL."""
from datetime import timedelta
import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class User(models.Model):
    """Custom user table used for authentication."""

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    suspend = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    ref_person_id = models.BigIntegerField(null=True)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return str(self.username)


class UserProfile(models.Model):
    """User profiles for tying user to personal data."""
    class MfaMethod(models.TextChoices):
        """ Choice options for MFA Methods."""
        AUTHENTICATOR = "authenticator", "authenticator"
        NONE = "none", "none"

    class SecretQuestions(models.TextChoices):
        """ Choice options for Secret Questions """
        QUESTION1 = (
            "What is your mother’s maiden name?",
            "What is your mother’s maiden name?"
            )
        QUESTION2 = (
            "What was the make and model of your first car?",
            "What was the make and model of your first car?"
            )
        QUESTION3 = (
            "Who was your childhood hero?",
            "Who was your childhood hero?"
            )
        QUESTION4 = (
            "In what city were you when you got your first job?",
            "In what city were you when you got your first job?"
            )
        QUESTION5 = (
            "What was your dream job as a child?", 
            "What was your dream job as a child?"
        )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name_first = models.CharField(max_length=255)
    name_middle = models.CharField(max_length=255, null=True, blank=True)
    name_last = models.CharField(max_length=255)
    mfa_enabled = models.BooleanField(default=False)
    mfa_method = models.CharField(
        max_length=20, choices=MfaMethod.choices, default=MfaMethod.NONE
    )
    mfa_secret_hash = models.CharField(max_length=255)
    mfa_verified_at = models.DateTimeField()
    secret_question_1 = models.CharField(
        max_length=255, choices=SecretQuestions.choices, blank=True
    )
    secret_answer_1_hash = models.CharField(max_length=255)
    secret_question_2 = models.CharField(
        max_length=255, choices=SecretQuestions.choices, blank=True
    )
    secret_question_2_hash = models.CharField()
    failed_logins = models.BigIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.secret_question_1 and self.secret_question_2:
            if self.secret_question_1 == self.secret_question_2:
                raise ValidationError("Secret questions must be different.")

    def __str__(self):  # pragma: no cover - simple representation
        return f"Profile({self.user.username})"


class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_attempts")
    time = models.DateTimeField()
    successful = models.BooleanField()
    ip_address = models.CharField(max_length=255)

    def __str__(self):  # pragma: no cover - simple representation
        return f"Attempt({self.user.username} {self.time})"


class Organization(models.Model):
    name = models.BigIntegerField()
    ref_location_id = models.BigIntegerField()

    def __str__(self):  # pragma: no cover - simple representation
        return str(self.name)


class Role(models.Model):
    name = models.BigIntegerField()

    def __str__(self):  # pragma: no cover - simple representation
        return str(self.name)


class UserOrganization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organizations")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    date_joined = models.DateTimeField()

    def __str__(self):  # pragma: no cover - simple representation
        return f"{self.user.username}-{self.organization.id}"


class CryptaGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):  # pragma: no cover - simple representation
        return str(self.name)


class UserCryptaGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(CryptaGroup, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover - simple representation
        return f"{self.user.username}-{self.group.id}"


class QueryPermission(models.Model):
    class ResourceType(models.TextChoices):
        PERSON = "person", "Person"
        LOCATION = "location", "Location"
        PRIEST_DETAIL = "priest_detail", "Priest Detail"
        CHURCH_DETAIL = "church_detail", "Church Detail"
        SCHOOL_DETAIL = "school_detail", "School Detail"
        # Add more here

    class AccessType(models.TextChoices):
        READ = "read", "Read"
        EXPORT = "export", "Export"
        WRITE = "write", "Write"
        CREATE = "create", "Create"
        FULL_CONTROL = "fullControl", "Full Control"

    group = models.ForeignKey(CryptaGroup, on_delete=models.CASCADE)
    resource_type = models.CharField(max_length=32, choices=ResourceType.choices)
    access_type = models.CharField(max_length=32, choices=AccessType.choices)
    view_limits = models.JSONField()
    filter_conditions = models.JSONField()

    def __str__(self):  # pragma: no cover - simple representation
        return f"Perm({self.group.id}-{self.resource_type}-{self.access_type})"


class Feature(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):  # pragma: no cover - simple representation
        return str(self.name)


class RoleFeature(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    create = models.BooleanField()
    read = models.BooleanField()
    update = models.BooleanField()
    delete = models.BooleanField()

    def __str__(self):  # pragma: no cover - simple representation
        return f"{self.role.id}-{self.feature.id}"


class Token(models.Model):
    class TokenType(models.TextChoices):
        ACCESS = "access", "access"
        REFRESH = "refresh", "refresh"
        RESET = "reset", "reset"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    type = models.CharField(max_length=20, choices=TokenType.choices)
    expiration = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    revoked = models.BooleanField(default=False)

    # Override save method of models
    def save(self, *args, **kwargs):
        if not self.expiration:
            if self.type == self.TokenType.ACCESS:
                self.expiration = timezone.now() + timedelta(hours=1)
            elif self.type in [self.TokenType.REFRESH, self.TokenType.RESET]:
                self.expiration = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):  # pragma: no cover - simple representation
        return f"{self.user.username}-{self.type}"


class OrganizationFeature(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    enabled_at = models.DateTimeField(default=timezone.now, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):  # pragma: no cover - simple representation
        return f"{self.organization.name}-{self.feature.name}"


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    used_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.token.type != Token.TokenType.RESET:
            raise ValidationError("only tokens of type 'reset' can be used for password resets")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):  # pragma: no cover - simple representation
        return f"Reset({self.user.username})"


class UserStatusLog(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "active"
        INACTIVE = "inactive", "inactive"
        LOCKED = "locked", "locked"
        SUSPENDED = "suspended", "suspended"

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='status_logs')
    status = models.CharField(max_length=20, choices=Status.choices)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='status_changes_made')
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(timezone.now)

    def __str__(self):  # pragma: no cover - simple representation
        return f"{self.user.username}-{self.status}"
