#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socks
import datetime
from telethon.tl.types import UserStatusOnline
from telethon.tl.types import UserStatusRecently
from telethon.tl.types import UserStatusLastWeek
from telethon.tl.types import UserStatusLastMonth
from telethon.tl.types import UserStatusEmpty


# Your Telegram API_ID here
tg_api_id = 0

# Your Telegram API_HASH here
tg_api_hash = 'Your Telegram API_HASH here'

# Database file
db_file = 'database.db'

# Sessions
sessions = {
    'session_name':
        {
            'name': 'session_name',
            'area_code': '+1',
            'phone': '+12345678900',
            'proxy': (socks.SOCKS5, 'localhost', 1080),
        },
}

# Filter of UserStatus
# Tips: DO NOT put `UserStatusOffline` in this
filter_user_status_types = [
    UserStatusOnline,
    UserStatusRecently,
    UserStatusLastWeek,
    UserStatusLastMonth,
    UserStatusEmpty,
]

# UserStatusOffline `was_online` limit
# filter_user_status_offline_was_online_min = datetime.datetime.now() - datetime.timedelta(weeks=4)
filter_user_status_offline_was_online_min = None
filter_user_status_offline_was_online_max = None

# if display_name is too long, skip
filter_user_display_name_too_much_words_limit = 25

# user batch amount
rd_pending_users_amount_min = 25
rd_pending_users_amount_max = 35


# Source group list
source_groups = [
    'GROUP_USERNAME',
]

# destination group
destination_group = 'GROUP_USERNAME'


# random relax during inviting actions
rd_sleep_min = 10
rd_sleep_max = 30
