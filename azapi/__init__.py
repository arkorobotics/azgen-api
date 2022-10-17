#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/__init__.py

from fastapi import FastAPI

from .cors import add_cors_middleware
from .config import settings
from .endpoints import router
from .log import (logger, DEBUG, WARNING)
from .version import __version__

__all__ = ['register_endpoints', 'app_factory']


# Provide a central point for registering API endpoints
def register_endpoints(app):
    app.include_router(endpoints.router)


# App factory performs all tasks needed to generate a valid WSGI app
def app_factory():
    app = FastAPI(title="AZGen-API", version=__version__)
    add_cors_middleware(app)

    register_endpoints(app)

    if settings.debug:
        print("Debug Logging is Enabled")
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(WARNING)

    return app
