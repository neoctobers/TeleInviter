#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Title:  TeleInviter
# Author: @neoctobers
#
# Invite members, from `source_groups` to `destination_group`
# And avoid repetition from `existing_groups` and `destination_group`
#
# [Github]:
#     https://github.com/neoctobers/TeleInviter
#
# [Telegram Group]:
#     https://t.me/TeleInviter
#

import sys
import colorama
import conf
import console
import telethon
from telethon import TelegramClient
from telethon import sync
from telethon import errors
from telethon.tl.types import UserStatusOffline
from telethon.tl.functions.channels import JoinChannelRequest
from pprint import pprint


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


# Initialize colorama with auto-reset
colorama.init(autoreset=True)
print('starting...')

# Initialize clients
clients = {}
print(colorama.Fore.LIGHTCYAN_EX + '\n\nLaunching Session:')
for client_session in conf.client_sessions:
    # Launch
    sys.stdout.write('  "%s" ... ' % client_session)

    # Start the client
    c = TelegramClient(
        client_session,
        conf.tg_api_id,
        conf.tg_api_hash,
        proxy=conf.proxy,
    )
    c.start()

    # Confirm the user is authorized
    if c.is_user_authorized():
        clients[client_session] = c
        del c
        print(colorama.Fore.GREEN + 'DONE')
    else:
        # If it's not authorized, maybe need to do sth.?
        print(colorama.Fore.LIGHTRED_EX + 'NEED Auth!')


# Initialize the destination group dict, same keys as clients
destination_groups = {}
sys.stdout.write(colorama.Fore.LIGHTCYAN_EX + '\n\nDestination Group: ')
print('"%s"' % conf.destination_group)
for client_session in conf.client_sessions:
    # each session
    sys.stdout.write('  "%s" ... ' % client_session)

    # error when session user is banned
    try:
        g = clients[client_session].get_entity(conf.destination_group)

        # Join if not IN.
        if g.left:
            clients[client_session](JoinChannelRequest(g))
            print(colorama.Fore.LIGHTYELLOW_EX + 'JOINED')
        else:
            print(colorama.Fore.GREEN + 'IN')

        # Democracy
        if g.democracy:
            # All members can add members
            destination_groups[client_session] = g
        else:
            # Only admins can add members
            if (g.admin_rights is not None and g.admin_rights.invite_users):
                destination_groups[client_session] = g
            else:
                sys.stdout.write(colorama.Fore.LIGHTRED_EX + '    Have NO admin right to add a member,')
                print(colorama.Fore.LIGHTYELLOW_EX + ' session is REMOVED.')
                del clients[client_session]

    except ValueError as e:
        print(colorama.Fore.LIGHTRED_EX + 'ERROR')
        print(colorama.Fore.LIGHTRED_EX + '    %s' % e)
        print(colorama.Fore.LIGHTYELLOW_EX + '    Please make sure "%s" is NOT banned' % client_session)
        print('    session "%s" is removed from clients' % client_session)
        del clients[client_session]
        # sys.exit()
        pass


# Exit if there is no available client
if 0 == len(clients):
    print(colorama.Fore.LIGHTRED_EX + 'No client available...')
    sys.exit()


# OUTPUT: clients
print(colorama.Fore.LIGHTCYAN_EX + '\n\nThese clients have been launched:')
i = 1
for key, client in clients.items():
    print('%4d: "%s"' % (i, key))
    i = i + 1


# Ready to GO ?
if (input('\n\n\nReady to GO (y/n)?') not in ['y', 'yes']):
    sys.exit('\n\n')



# TODO: MANY THINGS
#
# ts = []
#
# # Start working...
# client0 = clients[conf.client_sessions[0]]
#
# participants = []
# for group_key in conf.source_groups:
#     print('---\nGroup - %s\n---' % group_key)
#
#     try:
#         g = client0.get_entity(group_key)
#         if not isinstance(g, telethon.tl.types.Channel):
#             print('is not a Channel')
#         else:
#             participants.extend(client0.get_participants(g, aggressive=True))
#             print('%d members found.' % len(participants))
#
#     except errors.rpcerrorlist.InviteHashInvalidError:
#         print('"%s"\n[Source group] The invite hash is invalid' % group_key)
#
# i = 0
# for u in participants:
#     # No bot
#     if u.bot is False:
#         if type(u.status) in conf.filter_user_status_types:
#             # Not UserStatusOffline
#             print('%6d: %d, %s, %s | %s' % (i, u.id, u.username, u.first_name, u.last_name))
#             print(u.status)
#         elif (isinstance(u.status, UserStatusOffline)):
#             # UserStatusOffline
#             if is_user_status_offline_passed(u.status.was_online):
#                 print('%6d: %d, %s, %s | %s' % (i, u.id, u.username, u.first_name, u.last_name))
#                 print(u.status)
#                 ts.append(u.status.was_online)
#
#     # Next
#     i = i + 1


c = clients[conf.client_sessions[0]]

console.embed(banner='\nconsole')
