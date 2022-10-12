#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/config.py

from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    root: str = "/"
    bind_host: str = "127.0.0.1"
    port: int = 8082


settings = Settings()
