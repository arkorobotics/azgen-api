#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/cors.py

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://activation.zone",
    "http://www.activation.zone",
    "https://activation.zone",
    "https://www.activation.zone",
    "http://localhost:8082",
    "https://localhost:8082",
    "http://localhost:8080",
    "https://localhost:8080"
]


def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
