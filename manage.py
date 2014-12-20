#!/usr/bin/env python
# -*- coding: utf-8 -*-

from f6a_tw_backend.constants import *
from f6a_tw_backend.django_constants import *

import os
import sys
import argparse

from f6a_tw_backend import cfg
from f6a_tw_backend import settings


def parse_args():
    ''' '''
    parser = argparse.ArgumentParser(description='f6a_tw_backend')
    parser.add_argument('args', nargs='*', type=str, default=[], help="args")
    parser.add_argument('-i', '--ini', type=str, required=False, default='development.ini', help="ini filename")

    (args, unknown_args) = parser.parse_known_args()

    return (S_OK, args, unknown_args)


def _main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "f6a_tw_backend.settings")

    (error_code, args, unknown_args) = parse_args()

    cfg.init({"ini_filename": args.ini})

    settings.SECRET_KEY = cfg.config.get('django_secret_key', 'DEFAULT_DJANGO_SECRET_KEY')

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    _main()
