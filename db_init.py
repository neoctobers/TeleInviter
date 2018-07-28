# coding:utf-8
from db import *


db.connect()
db.create_tables([Invite, KeyPosition])

print('Database: initialization complete!')
