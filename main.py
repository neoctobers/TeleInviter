#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Title:  TeleInviter
# Author: @neoctobers
#
# Invite members, from (many) `source_groups` to (one) `destination_group`
# And avoid repetition from `destination_group`
#
# [Github]:
#     https://github.com/neoctobers/TeleInviter
#
# [Telegram Group]:
#     https://t.me/TeleInviter
#

import sys
import time
import random
import colorama
import telethon
import conf
import console
import db
from telethon import sync
from telethon import errors
from telethon.tl.types import UserStatusOffline
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from pprint import pprint



def get_user_display_name(u):
    """Get `display_name` for a user

    Args:
        u: user

    Returns:
        A string
        example:
            'Donald J. Trump'
    """
    name = []
    if u.first_name:
        name.append(u.first_name)
    if u.last_name:
        name.append(u.last_name)
    return '|'.join(name)


def invite_user(u):
    """Invite user to destination_group

    Args:
        u: user
    """

    # SN, display_name
    sys.stdout.write('%6d > [%s] ... ' % (i, get_user_display_name(u)))

    # Find in db
    row = db.Invite.select().where(db.Invite.user_id == u.id).first()

    # No record in db
    if row is None:
        # Get a random session
        client_session = random.choice(client_sessions)

        # Echo
        sys.stdout.write(colorama.Fore.LIGHTYELLOW_EX + 'INVITE by "%s" ... ' % client_session)


        try:
            # Invite
            clients[client_session](InviteToChannelRequest(
                destination_groups[client_session],
                [u],
            ))

            # Save to db
            db.save_invite(u)

            # shows done
            sys.stdout.write(colorama.Fore.GREEN + 'DONE')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            print(colorama.Fore.LIGHTMAGENTA_EX + ' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except errors.rpcerrorlist.UserPrivacyRestrictedError:
            print(colorama.Fore.LIGHTRED_EX + 'error#0. UserPrivacyRestrictedError...')
        except errors.rpcerrorlist.ChatAdminRequiredError:
            print(colorama.Fore.LIGHTRED_EX + 'error#1. ChatAdminRequiredError...')
        except errors.rpcerrorlist.ChatIdInvalidError:
            print(colorama.Fore.LIGHTRED_EX + 'error#2. ChatIdInvalidError...')
        except errors.rpcerrorlist.InputUserDeactivatedError:
            print(colorama.Fore.LIGHTRED_EX + 'error#3. InputUserDeactivatedError...')
        except errors.rpcerrorlist.PeerIdInvalidError:
            print(colorama.Fore.LIGHTRED_EX + 'error#4. PeerIdInvalidError...')
        except errors.rpcerrorlist.UserAlreadyParticipantError:
            print(colorama.Fore.LIGHTRED_EX + 'error#5. UserAlreadyParticipantError...')
        except errors.rpcerrorlist.UserIdInvalidError:
            print(colorama.Fore.LIGHTRED_EX + 'error#6. UserIdInvalidError...')
        except errors.rpcerrorlist.UserNotMutualContactError:
            print(colorama.Fore.LIGHTRED_EX + 'error#7. UserNotMutualContactError...')
        except errors.rpcerrorlist.UsersTooMuchError:
            print(colorama.Fore.LIGHTRED_EX + 'error#8. UsersTooMuchError...')
        except errors.rpcerrorlist.PeerFloodError:
            sys.stdout.write(colorama.Fore.LIGHTRED_EX + 'error#9. PeerFloodError...')
            print('Retry after 2 Mins...')
            time.sleep(120)
            invite_user(u)
    else:
        print(colorama.Fore.GREEN + 'skipped')


def is_user_status_offline_passed(t):
    """Check UserStatusOffline `was_online` limit

    Args:
        t: datetime

    Returns:
        boolean
    """
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


# Initialize colorama with auto-reset on
colorama.init(autoreset=True)


# OUTPUT: starting
print('starting...')


# Initialize `clients` dict
clients = {}
client_sessions = []
print(colorama.Fore.LIGHTCYAN_EX + '\n\nLaunching Clients:')
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

    # Confirm authorized or start the client (login)
    if c.is_user_authorized():
        # Authorized
        clients[client_session] = c
        client_sessions.append(client_session)
        print(colorama.Fore.GREEN + 'DONE')
    else:
        # Need to login
        print(colorama.Fore.LIGHTYELLOW_EX + 'Need Login\n')
        print(colorama.Fore.LIGHTMAGENTA_EX + 'Session login for "%s"' % client_session)

        # Login
        c.start()

        # Verify Login
        if c.is_user_authorized():
            clients[client_session] = c
            client_sessions.append(client_session)
            print(colorama.Fore.GREEN + 'Session login for "%s" is SUCCESSFUL' % client_session)
        else:
            print(colorama.Fore.LIGHTRED_EX + 'Session login for "%s" is FAILED' % client_session)


# Exit if there is no available client
if 0 == len(clients):
    print(colorama.Fore.LIGHTRED_EX + 'No client available...')
    sys.exit()


# Initialize `destination_groups` dict, same keys as clients
destination_groups = {}
sys.stdout.write(colorama.Fore.LIGHTCYAN_EX + '\n\nDestination Group: ')
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
    i += 1
del i


# Verify `source_groups`
source_groups = []
print(colorama.Fore.LIGHTCYAN_EX + '\n\nVerify Source Groups:')
for group_key in conf.source_groups:
    print('  "%s" ... ' % group_key)
    try:
        g = clients[client_sessions[0]].get_entity(group_key)
        source_groups.append(group_key)
        print(colorama.Fore.GREEN + '    %s' % g.title)
    except errors.rpcerrorlist.InviteHashInvalidError as e:
        sys.stdout.write(colorama.Fore.LIGHTRED_EX + '    [InviteHashInvalidError] ')
        print(colorama.Fore.LIGHTYELLOW_EX + '%s' % e)
    except ValueError as e:
        sys.stdout.write(colorama.Fore.LIGHTRED_EX + '    [ValueError] ')
        print(colorama.Fore.LIGHTYELLOW_EX + '%s' % e)


# OUTPUT: source_groups
print(colorama.Fore.LIGHTCYAN_EX + '\n\nThese Source Groups have been verified:')
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
print(colorama.Fore.LIGHTCYAN_EX + '\n\nLoading participants:')
for client_session, client in clients.items():
    print('\n- %s:' % client_session)
    participants[client_session] = []
    for group_key in source_groups:
        sys.stdout.write('  "%s" ... ' % group_key)
        ps = client.get_participants(group_key, aggressive=True)
        participants[client_session].extend(ps)
        print(colorama.Fore.GREEN + '%d members' % len(ps))
        del ps

    # members amount
    print(colorama.Fore.LIGHTYELLOW_EX + '    %d members' % len(participants[client_session]))


# Ready to GO ?
if (input('\n\n\nReady to GO (y/n)? ') not in ['y', 'yes']):
    sys.exit('\n\n')


# Start inviting
print(colorama.Fore.LIGHTCYAN_EX + '\n\nStarting inviting:')
i = 0
for u in participants[client_sessions[0]]:
    if u.bot is False:
        # skip bots
        if len(get_user_display_name(u)) > conf.filter_user_display_name_too_much_words_limit:
            # avoid spam, who has a very long name
            pass
        elif type(u.status) in conf.filter_user_status_types:
            # Not UserStatusOffline
            invite_user(u)
        elif (isinstance(u.status, UserStatusOffline) and is_user_status_offline_passed(u.status.was_online)):
            # UserStatusOffline
            invite_user(u)

    # Next
    i += 1
del i


# embed & console
console.embed(banner='\nconsole')

