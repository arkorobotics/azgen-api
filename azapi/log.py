#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/log.py

import logging

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

logger = logging.getLogger('azapi')

# Set Defaults
logger.setLevel(logging.DEBUG)
_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)
_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_ch.setFormatter(_formatter)
logger.addHandler(_ch)


def debug(*args, **kwargs):
    logger.debug(*args, **kwargs)


def info(*args, **kwargs):
    logger.info(*args, **kwargs)


def warning(*args, **kwargs):
    logger.warning(*args, **kwargs)


def error(*args, **kwargs):
    logger.error(*args, **kwargs)


def critical(*args, **kwargs):
    logger.critical(*args, **kwargs)


def exception(*args, **kwargs):
    logger.exception(*args, **kwargs)
