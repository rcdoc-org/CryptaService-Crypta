# models.py
from datetime import datetime, timezone
import os
from mongoengine import *
from passlib.hash import argon2
from passlib.context import CryptContext
from flask_security import UserMixin, RoleMixin

pwd_ctx = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__rounds=4,
)

class Role(Document, RoleMixin):
    name        = StringField(max_length=100, unique=True)
    description = StringField(max_length=255)

class User(Document, UserMixin):
    email      = EmailField(required=True, unique=True)
    password   = StringField(required=True)
    active     = BooleanField(default=True)
    roles      = ListField(ReferenceField(Role), default=[])
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    last_login = DateTimeField()

    fs_uniquifier = UUIDField(binary=False, default=uuid.uuid4, unique=True)


    meta = {
      "indexes": [
          {"fields": ["email"], "unique": True},
          {"fields": ["roles", "active"]},
          ]
    }
    
    def set_password(self, raw):
        self.password = pwd_ctx.hash(raw)
    
    def check_password(self, raw):
        return pwd_ctx.verify(raw, self.password)

class Profile(Document):
    user       = ReferenceField(User, reverse_delete_rule=CASCADE)
    first_name = StringField()
    last_name  = StringField()
    avatar_url = URLField()

class Token(Document):
    user        = ReferenceField(User, required=True)
    token       = StringField(required=True, unique=True)
    type        = StringField(choices=['confirm','reset'])
    created_at  = DateTimeField(default=lambda: datetime.now(timezone.utc))
    meta = {
        'indexes': [
            {'fields': ['created_at'], 'expireAfterSeconds': 3600}
        ]
    }
    
class OAuthAccount(Document):
    user             = ReferenceField(User, reverse_delete_rule=CASCADE)
    provider         = StringField(required=True, choices=["google","microsoft","azuread"])
    provider_user_id = StringField(required=True)   # e.g. sub/email
    access_token     = StringField()
    refresh_token    = StringField()
    expires_at       = DateTimeField()              # aware UTC datetime
    meta = {
        "indexes": [
            {"fields": ["provider","provider_user_id"], "unique": True}
        ]
    }
