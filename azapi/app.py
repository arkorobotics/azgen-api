#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/app.py

from .env import read_env
from . import app_factory

# The application is being loaded as a WSGI application, load env vars and generate the app
read_env()
app = app_factory()
