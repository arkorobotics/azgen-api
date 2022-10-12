#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/env.py

from os import environ

from .config import settings
from .log import warning


# Read settings from the environment and apply it to the app config
def read_env():
    try:
        debug_mode = int(environ.get('AZAPI_DEBUG', '0')) > 0
    except ValueError:
        warning('Value provided by AZAPI_DEBUG was non-integer. Failing over to default (False)')
        debug_mode = False
    try:
        port = int(environ.get('AZAPI_PORT', f'{settings.port}'))
    except ValueError:
        warning(f'Value provided by AZAPI_PORT was non-integer. Failing over to default ({settings.port})')
        port = settings.port

    settings.debug = debug_mode
    settings.port = port
