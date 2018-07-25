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
from telethon import sync
from telethon import errors
from telethon.tl.types import UserStatusOffline
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from pprint import pprint

import db


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
FORE_CYAN = colorama.Fore.LIGHTCYAN_EX
FORE_YELLOW = colorama.Fore.LIGHTYELLOW_EX
FORE_GREEN = colorama.Fore.GREEN
FORE_RED = colorama.Fore.LIGHTRED_EX
FORE_MAGENTA = colorama.Fore.LIGHTMAGENTA_EX


# OUTPUT: starting
print('starting...')


# Initialize `clients` dict
clients = {}
client_sessions = []
print(FORE_CYAN + '\n\nLaunching Clients:')
for client_session in conf.client_sessions:
    # Launch
    sys.stdout.write('  "%s" ... ' % client_session)

    # Create a Telegram Client
    c = telethon.TelegramClient(
        client_session,
        conf.tg_api_id,
        conf.tg_api_hash,
        proxy=conf.proxy,
    )
    c.connect()
    if c.is_user_authorized():
        # Authorized
        clients[client_session] = c
        client_sessions.append(client_session)
        print(FORE_GREEN + 'DONE')
    else:
        # Need to login
        print(FORE_YELLOW + 'Need Login\n')
        print(FORE_MAGENTA + 'Session login for "%s"' % client_session)
        c.start()

        # Verify Login
        if c.is_user_authorized():
            clients[client_session] = c
            client_sessions.append(client_session)
            print(FORE_GREEN + 'Session login for "%s" is SUCCESSFUL' % client_session)
        else:
            print(FORE_RED + 'Session login for "%s" is FAILED' % client_session)


# Exit if there is no available client
if 0 == len(clients):
    print(FORE_RED + 'No client available...')
    sys.exit()


# Initialize `destination_groups` dict, same keys as clients
destination_groups = {}
sys.stdout.write(FORE_CYAN + '\n\nDestination Group: ')
print('"%s"' % conf.destination_group)
for client_session, client in clients.items():
    # each session
    sys.stdout.write('  "%s" ... ' % client_session)

    # error when session user is banned
    try:
        g = client.get_entity(conf.destination_group)

        # Join if not IN.
        if g.left:
            client(JoinChannelRequest(g))
            print(FORE_YELLOW + 'JOINED')
        else:
            print(FORE_GREEN + 'IN')

        # Democracy
        if g.democracy:
            # All members can add members
            destination_groups[client_session] = g
        else:
            # Only admins can add members
            if (g.admin_rights is not None and g.admin_rights.invite_users):
                destination_groups[client_session] = g
            else:
                sys.stdout.write(FORE_RED + '    Have NO admin right to add a member,')
                print(FORE_YELLOW + ' session is REMOVED.')
                del clients[client_session]

    except ValueError as e:
        print(FORE_RED + 'ERROR')
        print(FORE_RED + '    %s' % e)
        print(FORE_YELLOW + '    Please make sure "%s" is NOT banned' % client_session)
        print('    session "%s" is removed from clients' % client_session)
        del clients[client_session]
        # sys.exit()
        pass


# Exit if there is no available client
if 0 == len(clients):
    print(FORE_RED + 'No client available...')
    sys.exit()


# OUTPUT: clients
print(FORE_CYAN + '\n\nThese clients have been launched:')
i = 1
for key, client in clients.items():
    print('%4d: "%s"' % (i, key))
    i += 1
del i


# Verify `source_groups`
source_groups = []
print(FORE_CYAN + '\n\nVerify Source Groups:')
c = clients[client_sessions[0]]
for group_key in conf.source_groups:
    print('  "%s" ... ' % group_key)
    try:
        g = c.get_entity(group_key)
        source_groups.append(group_key)
        print(FORE_GREEN + '    %s' % g.title)
    except errors.rpcerrorlist.InviteHashInvalidError as e:
        sys.stdout.write(FORE_RED + '    [InviteHashInvalidError] ')
        print(FORE_YELLOW + '%s' % e)
    except ValueError as e:
        sys.stdout.write(FORE_RED + '    [ValueError] ')
        print(FORE_YELLOW + '%s' % e)


# OUTPUT: source_groups
print(FORE_CYAN + '\n\nThese Source Groups have been verified:')
i = 1
for group_key in source_groups:
    print('%4d: "%s"' % (i, group_key))
    i += 1
del i


# Continue
if (input('\n\n\nLOAD participants (y/n)? ') not in ['y', 'yes']):
    sys.exit('\n\n')


# Initialize `participants` dict
participants = {}
print(FORE_CYAN + '\n\nLoading participants:')
for client_session, client in clients.items():
    print('\n- %s:' % client_session)
    participants[client_session] = []
    for group_key in source_groups:
        sys.stdout.write('  "%s" ... ' % group_key)
        ps = client.get_participants(group_key, aggressive=True)
        participants[client_session].extend(ps)
        print(FORE_GREEN + '%d members' % len(ps))

    print(FORE_YELLOW + '    %d members' % len(participants[client_session]))


# Ready to GO ?
if (input('\n\n\nReady to GO (y/n)? ') not in ['y', 'yes']):
    sys.exit('\n\n')


def get_user_display_name(u):
    name = []
    if u.first_name:
        name.append(u.first_name)
    if u.last_name:
        name.append(u.last_name)
    return ' | '.join(name)


def invite_user(u):
    sys.stdout.write('%6d: %s ... ' % (i, get_user_display_name(u)))

    row = db.Invite.select().where(db.Invite.user_id == u.id).first()

    if row is None:
        invite = db.save_invite(u)
        print(FORE_YELLOW + 'TO BE INVITED')
    else:
        print(FORE_GREEN + 'skipped')


# Start inviting
print(FORE_CYAN + '\n\nStarting inviting:')
i = 0
for u in participants[client_sessions[0]]:
    if u.bot is False:
        if len(get_user_display_name(u)) > conf.filter_user_display_name_too_much_words_limit:
            pass
        elif type(u.status) in conf.filter_user_status_types:
            # Not UserStatusOffline
            invite_user(u)
        elif (isinstance(u.status, UserStatusOffline)):
            # UserStatusOffline
            if is_user_status_offline_passed(u.status.was_online):
                invite_user(u)

    # Next
    i += 1


# embed & console
console.embed(banner='\nconsole')

