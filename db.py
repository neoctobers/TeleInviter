# coding:utf-8
from peewee import *
import time


db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db

class Invite(BaseModel):
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
        return self.full_name


def save_invite(u):
    invite, created = Invite.get_or_create(
        user_id=u.id,
        defaults={
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'updated_': int(time.time()),
        },
    )

    update = False
    if invite.username != u.username:
        invite.username = u.username
        update = True
    if invite.first_name != u.first_name:
        invite.first_name = u.first_name
        update = True
    if invite.last_name != u.last_name:
        invite.last_name = u.last_name
        update = True
    if update:
        invite.updated_ = int(time.time())
        invite.save()

    return invite
