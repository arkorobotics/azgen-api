#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/cli.py

import os
from argparse import ArgumentParser

import uvicorn

from .config import settings
from .env import read_env
from .version import __version__


def _parse_args():
    parser = ArgumentParser(description="Azgen API CLI. This starts a dev server for the API.")
    parser.add_argument('-b', '--bind',
                        default=settings.bind_host,
                        help='Host to Bind to. Default: %(default)s')
    parser.add_argument('-p', '--port',
                        default=settings.port,
                        type=int,
                        help='Port to run the API on. Default: %(default)s')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Print debug messages.')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='v{}'.format(__version__),
                        help='Print version and exit.')
    args = parser.parse_args()
    return args


def _generate_config():
    read_env()
    args = _parse_args()

    settings.bind_host = args.bind
    settings.port = args.port
    settings.debug = args.debug or settings.debug


def main():
    _generate_config()

    if settings.debug:
        # To enable active reload, this has to be saved to an env var
        os.environ["AZAPI_DEBUG"] = "1"

    log_level = "info"
    if settings.debug:
        log_level = "debug"

    uvicorn.run("azapi.app:app",
                host=settings.bind_host,
                port=settings.port,
                log_level=log_level,
                reload=True,
                debug=settings.debug)
