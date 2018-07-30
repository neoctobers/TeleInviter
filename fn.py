#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import colorama


# Initialize colorama with auto-reset on
colorama.init(autoreset=True)


def print_text(value):
    print('%s' % value)
    return

def stdout_text(value):
    sys.stdout.write('%s' % value)
    return

def print_success(value):
    print(colorama.Fore.GREEN + '%s' % value)
    return

def stdout_success(value):
    sys.stdout.write(colorama.Fore.GREEN + '%s' % value)
    return

def print_error(value):
    print(colorama.Fore.LIGHTRED_EX + '%s' % value)
    return

def stdout_error(value):
    sys.stdout.write(colorama.Fore.LIGHTRED_EX + '%s' % value)
    return

def print_warning(value):
    print(colorama.Fore.LIGHTYELLOW_EX + '%s' % value)
    return

def stdout_warning(value):
    sys.stdout.write(colorama.Fore.LIGHTYELLOW_EX + '%s' % value)
    return

def print_info(value):
    print(colorama.Fore.LIGHTMAGENTA_EX + '%s' % value)
    return

def stdout_info(value):
    sys.stdout.write(colorama.Fore.LIGHTMAGENTA_EX + '%s' % value)
    return

def print_title(value):
    print(colorama.Fore.LIGHTCYAN_EX + '%s' % value)
    return

def stdout_title(value):
    sys.stdout.write(colorama.Fore.LIGHTCYAN_EX + '%s' % value)
    return
