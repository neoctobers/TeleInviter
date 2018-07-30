# coding:utf-8
import time
import conf
import colorama
import fn
from peewee import *


db = SqliteDatabase(conf.db_file, pragmas={'cache_size': 0})

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    updated_ = IntegerField(null=True)

    @property
    def display_name(self):
        name = []
        if self.first_name:
            name.append(self.first_name)
        if self.last_name:
            name.append(self.last_name)
        return ' '.join(name)

    @property
    def call_name(self):
        if self.username:
            return '@%s' % self.username
        return self.display_name

class Invite(User):
    pass

class UserPrivacyRestricted(User):
    pass

class UserNotMutual(BaseModel):
    user_id = IntegerField()
    area_code = CharField()
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    updated_ = IntegerField(null=True)

    @property
    def display_name(self):
        name = []
        if self.first_name:
            name.append(self.first_name)
        if self.last_name:
            name.append(self.last_name)
        return ' '.join(name)

    @property
    def call_name(self):
        if self.username:
            return '@%s' % self.username
        return self.display_name

def confirm_tables():
    db.connect()
    db.create_tables([Invite, UserPrivacyRestricted, UserNotMutual])
    return

def save_invite(u):
    user, created = Invite.get_or_create(
        user_id=u.id,
        defaults={
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'updated_': int(time.time()),
        },
    )

    update = False
    if user.username != u.username:
        user.username = u.username
        update = True
    if user.first_name != u.first_name:
        user.first_name = u.first_name
        update = True
    if user.last_name != u.last_name:
        user.last_name = u.last_name
        update = True
    if update:
        user.updated_ = int(time.time())
        user.save()

    return user

def save_user_privacy_restricted(u):
    user, created = UserPrivacyRestricted.get_or_create(
        user_id=u.id,
        defaults={
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'updated_': int(time.time()),
        },
    )

    update = False
    if user.username != u.username:
        user.username = u.username
        update = True
    if user.first_name != u.first_name:
        user.first_name = u.first_name
        update = True
    if user.last_name != u.last_name:
        user.last_name = u.last_name
        update = True
    if update:
        user.updated_ = int(time.time())
        user.save()

    return user

def save_user_not_mutual(u, area_code):
    user, created = UserNotMutual.get_or_create(
        user_id=u.id,
        area_code=area_code,
        defaults={
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'area_code': area_code,
            'updated_': int(time.time()),
        },
    )

    update = False
    if user.username != u.username:
        user.username = u.username
        update = True
    if user.first_name != u.first_name:
        user.first_name = u.first_name
        update = True
    if user.last_name != u.last_name:
        user.last_name = u.last_name
        update = True
    if user.area_code != area_code:
        user.area_code = area_code
        update = True
    if update:
        user.updated_ = int(time.time())
        user.save()

    return user




