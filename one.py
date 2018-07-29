#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import conf
import console
import colorama

from TeleInviter import TeleInviter
from pprint import pprint

if __name__ == '__main__':

    # Initialize colorama with auto-reset on
    colorama.init(autoreset=True)

    # print(colorama.Fore.LIGHTCYAN_EX + '\nLaunching Clients:')
    #
    # clients = {}
    # for key, client_session in conf.sessions.items():
    #     clients[key] = TeleInviter(client_session)

    i = TeleInviter(conf.sessions['richard'])
    i.set_source_groups([
        'https://t.me/three001',
        'https://t.me/dalubocai',
    ])
    i.set_destination_group('https://t.me/asilentgroup')
    i.start()

console.embed(banner='\n\nconsole')
