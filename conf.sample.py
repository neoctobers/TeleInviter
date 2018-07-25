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

# Proxy configuration here, or leave it as None
#proxy = None
proxy = (socks.SOCKS5, 'localhost', 1088)

# multi-client-session keys
client_sessions = [
    'YOUR_SESSION_KEYS',
]

# Existing group list
existing_groups = []

# source list (group or supergroup)
source_groups = [
    'ENTITY_USERNAME',
]

# destination (group or supergroup)
destination_group = 'ENTITY_USERNAME'

# Filter of UserStatus
# Tips: DO NOT put `UserStatusOffline` in this
filter_user_status_types = [
    UserStatusOnline,
    UserStatusRecently,
    UserStatusLastWeek,
    # UserStatusLastMonth,
    # UserStatusEmpty,
]

# UserStatusOffline `was_online` limit
filter_user_status_offline_was_online_min = datetime.datetime.now() - datetime.timedelta(weeks=4)
filter_user_status_offline_was_online_max = None

# if display_name is too long, skip
filter_user_display_name_too_much_words_limit = 25

# random relax during inviting actions
rd_sleep_min = 3
rd_sleep_max = 10

