#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Title:  TeleInviter
# Author: @neoctobers
#
# Invite members, from `source_groups` to `destination_group`
#
# Github: https://github.com/neoctobers/TeleInviter
# Telegram Group: https://t.me/https://t.me/TeleInviter
#

import sys
import conf
import console
from pprint import pprint
from telethon import TelegramClient
from telethon import sync
from telethon import errors
from telethon.tl.types import UserStatusOffline


def is_user_status_offline_passed(t):
    if (
            (conf.filter_user_status_offline_was_online_min is None or t >= conf.filter_user_status_offline_was_online_min)
            and
            (conf.filter_user_status_offline_was_online_max is None or t <= conf.filter_user_status_offline_was_online_max)
    ):
        # t >= `filter_user_status_offline_was_online_min` if it was set
        # AND
        # t <= `filter_user_status_offline_was_online_max` if it was set
        return True

    # Or return False
    return False


# initialize clients
clients = {}

for client_session in conf.client_sessions:
    # Launch
    print('[Launching Session]: %s ...' % client_session)

    clients[client_session] = TelegramClient(
        client_session,
        conf.tg_api_id,
        conf.tg_api_hash,
        proxy=conf.proxy,
    ).start()

    # Authorized Confirm
    if clients[client_session].is_user_authorized():
        print('  %s' % clients[client_session])
    else:
        print('  NEED Auth!')

    # blank line
    print()

ts = []

# count clients & start working
if len(clients):
    print('%d client(s) initialized...' % len(clients))

    c0 = clients[conf.client_sessions[0]]
    c1 = clients[conf.client_sessions[1]]

    g0 = c0.get_entity(conf.source_groups[0])
    g1 = c1.get_entity(conf.source_groups[0])

    # ps = c.get_participants(conf.source_groups[0], aggressive=True)
    #
    # i = 0
    # for u in ps:
    #     # No bot
    #     if u.bot is False:
    #         if type(u.status) in conf.filter_user_status_types:
    #             # Not UserStatusOffline
    #             print('%d: %s, %s | %s' % (i, u.username, u.first_name, u.last_name))
    #             print(u.status)
    #         elif (isinstance(u.status, UserStatusOffline)):
    #             # UserStatusOffline
    #             if is_user_status_offline_passed(u.status.was_online):
    #                 print('%d: %s, %s | %s' % (i, u.username, u.first_name, u.last_name))
    #                 print(u.status)
    #                 ts.append(u.status.was_online)
    #
    #     # Next
    #     i = i + 1
    #     pass

    console.embed(banner='\nconsole')

else:
    sys.exit('No client available...')
