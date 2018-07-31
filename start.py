#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import conf
import fn
import console
import colorama

import TeleDb
import TeleErrors

from TeleInviter import TeleInviter
from pprint import pprint


if __name__ == '__main__':
    colorama.init(autoreset=True)
    TeleDb.confirm_tables()

    clients = {}
    for key, client_session in conf.sessions.items():
        clients[key] = TeleInviter(client_session, db=TeleDb)
        clients[key].set_source_groups(conf.source_groups)
        clients[key].set_destination_group(conf.destination_group)

        try:
            clients[key].start()
        except TeleErrors.PeerFloodError:
            print('Client "%s" game over.' % key)

    # i = TeleInviter(conf.sessions['heyongchao'], db=TeleDb)
    # i.set_source_groups(conf.source_groups)
    # i.set_destination_group(conf.destination_group)
    #
    # try:
    #     i.start()
    # except TeleErrors.PeerFloodError:
    #     sys.exit('Game over.')


# console.embed(banner='\n\nconsole')
