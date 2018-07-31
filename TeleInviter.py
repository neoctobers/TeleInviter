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
import fn
import TeleErrors
from telethon.tl.types import UserStatusOffline
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import InviteToChannelRequest


class TeleInviter():
    def __init__(self, client_session=None, db=None):
        colorama.init(autoreset=True)
        self._client = self._init_client(client_session)
        self._client_name = client_session['name']
        self._area_code = client_session['area_code']
        self._me = self._client.get_me()
        self._db = db
        self._source_groups = []
        self._destination_group = None
        self._destination_groups = []
        self._pending_users = []

    @property
    def client(self):
        return self._client

    @property
    def client_name(self):
        return self._client_name

    @property
    def me(self):
        return self._me

    @property
    def db(self):
        return self._db

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
            except telethon.errors.rpcerrorlist.InviteHashInvalidError as e:
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
            fn.print_title('START INVITING, from %d source_group(s) to 1 destination_group' % len(self._source_groups))
            fn.print_text('------ ------ ------ ------\n')

            self._load_and_save_participants_from_destination_group()

            # Start working...
            for source_group in self._source_groups:
                fn.print_title('\nIMPORTING PARTICIPANTS from SOURCE_GROUP.')
                fn.print_text('  #%d / %s' % (source_group.id, source_group.username))
                fn.stdout_warning('    %s ...' % source_group.title)
                participants = self._client.get_participants(source_group, aggressive=True)
                fn.print_success(' %d members.' % len(participants))

                for user in participants:
                    if user.bot is False:
                        if len(self._get_user_display_name(user)) > conf.filter_user_display_name_too_much_words_limit:
                            # avoid spam, who has a very long name
                            pass
                        elif type(user.status) in conf.filter_user_status_types:
                            # Not UserStatusOffline
                            self._pend_user(user)
                        elif (
                                isinstance(user.status, UserStatusOffline) and
                                self._is_user_status_offline_passed(user.status.was_online)
                        ):
                            # UserStatusOffline
                            self._pend_user(user)

                    if len(self._pending_users) > random.randint(conf.rd_pending_users_amount_min, conf.rd_pending_users_amount_max):
                        self._do_batch_invite()
        return

    def _pend_user(self, user):
        """Pend a user to pool if not in database

        Args:
            user: user

        Returns:
            boolean
        """
        if self._db.Invite.select().where(self._db.Invite.user_id == user.id).first():
            return False

        if self._db.UserPrivacyRestricted.select().where(self._db.UserPrivacyRestricted.user_id == user.id).first():
            return False

        if self._db.UserNotMutual.select().where(self._db.UserNotMutual.user_id == user.id, self._db.UserNotMutual.area_code == self._area_code).first():
            return False

        self._pending_users.append(user)
        return True

    def _do_batch_invite(self):
        fn.print_warning('\n  INVITE %d users:' % len(self._pending_users))

        # call the roll
        for user in self._pending_users:
            fn.print_text('    #.%d > %s' % (user.id, self._get_user_console_name(user)))

        # batch invite
        fn.stdout_warning('      BATCH INVITE...')

        updates = self._client(InviteToChannelRequest(
            self._destination_group,
            self._pending_users
        ))

        if len(updates.users):
            fn.print_success(' %d/%d DONE' % (len(updates.users) - 1, len(self._pending_users)))

            # save invite to database
            for user in updates.users:
                if user.id != self._me.id:
                    fn.print_success('        #.%d > %s' % (user.id, self._get_user_console_name(user)))
                    self._db.save_invite(user)

            # clear pool
            self._pending_users = []

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info('  ... waiting %d secs ...' % sleeping_secs)
            time.sleep(sleeping_secs)
        else:
            print()
            for user in self._pending_users:
                self._do_one_invite(user)
            pass

    def _do_one_invite(self, user):
        fn.stdout_text('        INVITE user.#%d > %s...' % (user.id, self._get_user_console_name(user)))

        # Invite
        try:
            self._client(InviteToChannelRequest(
                self._destination_group,
                [user]
            ))

            # save to database
            self._db.save_invite(user)

            # shows done
            fn.stdout_success(' DONE')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)

        except ValueError as e:
            fn.print_error('\n              [ValueError] > ')
            fn.print_text(e)

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info('  ...waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.UserPrivacyRestrictedError:
            fn.stdout_error(' error.#0: UserPrivacyRestrictedError')
            self._db.save_user_privacy_restricted(user)

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.ChatAdminRequiredError:
            fn.stdout_error(' error.#1: ChatAdminRequiredError')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.ChatIdInvalidError:
            fn.stdout_error(' error.#2: ChatIdInvalidError')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.InputUserDeactivatedError:
            fn.stdout_error(' error.#3: InputUserDeactivatedError')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.PeerIdInvalidError:
            fn.stdout_error(' error.#4: PeerIdInvalidError')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.UserAlreadyParticipantError:
            fn.stdout_error(' error.#5: UserAlreadyParticipantError')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.UserIdInvalidError:
            fn.stdout_error(' error.#6: UserIdInvalidError')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.UserNotMutualContactError:
            fn.stdout_error(' error.#7: UserNotMutualContactError')
            self._db.save_user_not_mutual(user, self._area_code)

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.UsersTooMuchError:
            fn.stdout_error(' error.#8: UsersTooMuchError')

            # CPU sleep
            sleeping_secs = random.randint(conf.rd_sleep_min, conf.rd_sleep_max)
            fn.print_info(' waiting %d secs...' % sleeping_secs)
            time.sleep(sleeping_secs)
        except telethon.errors.rpcerrorlist.PeerFloodError as e:
            fn.stdout_error(' error.#9: PeerFloodError')
            fn.print_warning(' %s' % e)
            raise TeleErrors.PeerFloodError

    def _load_and_save_participants_from_destination_group(self):
        fn.print_title('\nLOAD & SAVE PARTICIPANTS from DESTINATION_GROUP.')
        fn.stdout_text('  "%s" ...' % self._destination_group.username)

        participants = self._client.get_participants(self._destination_group, aggressive=True)

        fn.print_success(' %d members.' % len(participants))

        i = 0
        for u in participants:
            if u.bot is False:
                self._db.save_invite(u)
                i += 1
                fn.stdout_warning('\r    %d saved.' % i)
                fn.stdout_text(' not include any bot.')
                sys.stdout.flush()
        print()

    @staticmethod
    def _is_user_status_offline_passed(t):
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
            # t >= `user_status_offline_was_online_min` if it was set
            # AND
            # t <= `user_status_offline_was_online_max` if it was set
            return True

        # Or return False
        return False

    @staticmethod
    def rd_sleep():
        pass
