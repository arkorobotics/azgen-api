#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/endpoints.py

import tempfile

from fastapi import (APIRouter, Response, status)
from starlette.responses import FileResponse

from .models import (AZRequest, AZResponse)
from .azgen import (get_bounds, get_cutoff_alt, get_az, get_gpx)
from .version import __version__
from .log import *

router = APIRouter()


# Basic API homepage, just tells us the version
@router.get("/")
def home():
    return f'AZAPI v{__version__}'


# From a valid AZRequest, perform the necessary calculations and return the expected polygon
@router.post("/", status_code=status.HTTP_200_OK, response_model=AZResponse)
def azgen(item: AZRequest, response: Response):
    bounds = get_bounds(item)
    cutoff_alt = get_cutoff_alt(item)
    az_geo = get_az(item, bounds)

    debug(f'Bounds: {bounds}')
    debug(f'Cutoff Alt: {cutoff_alt}')
    debug(f'AZ Data: {az_geo}')

    # Convert to string and remove altitude (0m)
    az_geo_string = str(az_geo)
    # az_geo_string = az_geo_string.replace(" 0", "")   # Legacy function call. May need it later.

    debug("Polygon String: ", az_geo_string)

    return {"az": az_geo_string}


# From a valid AZRequest, perform the necessary calculations and provide a gpx file download
@router.post("/gpx", status_code=status.HTTP_200_OK)
def download_gpx(item: AZRequest, response: FileResponse):
    debug("Go go gadget GPX!")
    bounds = get_bounds(item)
    cutoff_alt = get_cutoff_alt(item)

    # Python will clean up this temp directory once out of scope or garbage collected
    with tempfile.TemporaryDirectory() as tmpdir:
        az_geo = get_gpx(item, bounds, tmpdir)

        debug(f'Bounds: {bounds}')
        debug(f'Cutoff Alt: {cutoff_alt}')
        debug(f'AZ GPX Data: {az_geo}')

        return FileResponse(az_geo, media_type='application/gpx+xml', filename=item.summit_ref + '.gpx')
