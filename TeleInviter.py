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
import fn
from telethon import sync
from telethon import errors
from telethon.tl.types import PeerUser
from telethon.tl.types import UserStatusOffline
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from pprint import pprint


class TeleInviter():
    def __init__(
            self,
            client_session=None,
            # source_groups=None,
            # destination_groups=None,
    ):
        # Initialize colorama with auto-reset on
        colorama.init(autoreset=True)

        self._client = self._init_client(client_session)
        self._client_name = client_session['name']
        self._source_groups = []
        self._destination_group = None
        self._destination_groups = []

    @property
    def client(self):
        return self._client

    @property
    def client_name(self):
        return self._client_name

    @property
    def source_groups(self):
        return self._source_groups

    @property
    def destination_group(self):
        return self._destination_group

    @property
    def destination_groups(self):
        return self._destination_groups

    def _init_client(self, client_session):
        """Init a Telegram Client

        Args:
            client_session: dict

        Returns:
            A TelegramClient Object
        """
        fn.stdout_title('\nLaunching client "%s" ...' % client_session['name'])
        client = telethon.TelegramClient(client_session['name'], conf.tg_api_id, conf.tg_api_hash, proxy=client_session['proxy'])
        client.connect()
        if client.is_user_authorized():
            fn.print_success(' DONE')
            return client
        else:
            fn.print_warning(' Login by "%s"' % client_session['phone'])
            client.send_code_request(client_session['phone'])
            me = client.sign_in(client_session['phone'], input(colorama.Fore.LIGHTMAGENTA_EX + '    Login code: '))
            fn.print_success('    Login for "%s" is SUCCESSFUL' % self._get_user_display_name(me))

            if client.is_user_authorized():
                return client
            else:
                return self._init_client(client_session)

    def _get_user_console_name(self, u):
        """Get `console_name` for a user

        Args:
            u: user

        Returns:
            A string

            example:
                '[Donald|Trump]'
        """
        name = []
        if u.first_name:
            name.append(u.first_name)
        if u.last_name:
            name.append(u.last_name)
        return '[%s]' % '|'.join(name)

    def _get_user_display_name(self, u):
        """Get `display_name` for a user

        Args:
            u: user

        Returns:
            A string

            example:
                'Donald Trump'
        """
        name = []
        if u.first_name:
            name.append(u.first_name)
        if u.last_name:
            name.append(u.last_name)
        return '%s' % ' '.join(name)

    def set_source_groups(self, group_keys):
        """Set `source_groups` for this client

        Confirm the groups is exist.

        Args:
            group_keys: list

        Returns:
            int, number of groups
        """
        self._source_groups = []
        fn.print_title('\nsetting "%s" source groups:' % self._client_name)

        for group_key in group_keys:
            print('  "%s" ...' % group_key)

            try:
                group = self._client.get_entity(group_key)
                fn.print_success('    %s' % group.title)
                self._source_groups.append(group)
            except errors.rpcerrorlist.InviteHashInvalidError as e:
                fn.stdout_error('    [InviteHashInvalidError] ')
                fn.print_warning(e)
            except ValueError as e:
                fn.stdout_error('    [ValueError] ')
                fn.print_warning(e)

        return len(self._source_groups)

    def set_destination_group(self, key):
        """Set `destination_group` for this client

        Confirm the group is exist, and joined, and have the right to add a member.

        Args:
            group_keys: list

        Returns:
            int, number of groups
        """
        fn.print_title('\nsetting "%s" destination group:' % self._client_name)
        fn.stdout_text('  "%s" ...' % key)

        # error when session user is banned
        try:
            group = self._client.get_entity(key)

            # Join if not IN.
            if group.left:
                self._client(JoinChannelRequest(group))
                fn.print_warning(' JOINED')
            else:
                fn.print_success(' IN')

            # Democracy
            if group.democracy:
                # All members can add members
                fn.print_success('    %s' % group.title)
                self._destination_group = group
                return True
            else:
                # Only admins can add members
                if (group.admin_rights is not None and group.admin_rights.invite_users):
                    fn.print_success('    %s' % group.title)
                    self._destination_group = group
                    return True
                else:
                    fn.stdout_error('    Have NO admin right to add a member.')
                    fn.print_warning('    destination group invalid.')
                    return False

        except ValueError as e:
            fn.print_error(' ERROR')
            fn.print_error('    [ValueError] %s' % e)
            fn.print_warning('    Please make sure "%s" is NOT banned' % self._client_name)

    def set_destination_groups(self, group_keys):
        self._destination_groups = []
        sys.exit('function "set_destination_groups" is not available now...')

    def start(self):
        if len(self._source_groups) and self._destination_group:
            fn.print_text('\n------ ------ ------ ------')
            fn.print_warning('CLIENT "%s":' % self._client_name)
            fn.print_title('START INVITING, from %d source_groups to 1 destination_group' % len(self._source_groups))
            fn.print_text('------ ------ ------ ------\n')

            for source_group in self._source_groups:
                fn.print_title('\nIMPORTING PARTICIPANTS of SOURCE_GROUP.')
                fn.print_text('  #%d / %s' % (source_group.id, source_group.username))
                fn.stdout_warning('    %s ...' % source_group.title)
                participants = self._client.get_participants(source_group, aggressive=True)
                fn.print_success(' %d members.' % len(participants))
        return

