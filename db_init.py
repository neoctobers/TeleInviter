# coding:utf-8
from db import *


db.connect()
db.create_tables([Invite])

print('Database: initialization complete!')
