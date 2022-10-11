from fastapi import FastAPI, Response, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .models import AZRequest, AZResponse, AZGPXRequest, AZGPXResponse
from .azgen import get_bounds, get_cutoff_alt, get_az, get_gpx
from .verison import __version__

import tempfile
from os import path
import os

app = FastAPI()

origins = ["http://activation.zone", "http://www.activation.zone",
"https://activation.zone", "https://www.activation.zone", 
"http://localhost:8082", "https://localhost:8082",  
"http://localhost:8080", "https://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return f'AZAPI v{__version__}'


@app.post("/", status_code=status.HTTP_200_OK, response_model=AZResponse)
def azgen(item: AZRequest, response: Response):
    bounds = get_bounds(item)
    cutoff_alt = get_cutoff_alt(item)
    az_geo = get_az(item, bounds)

    print(f'Bounds: {bounds}')
    print(f'Cutoff Alt: {cutoff_alt}')
    print(f'AZ Data: {az_geo}')

    # Convert to string and remove altitude (0m)
    az_geo_string = str(az_geo)
    # az_geo_string = az_geo_string.replace(" 0", "")   # Legacy function call. May need it later.

    print("Polygon String: ", az_geo_string)
    
    return { "az": az_geo_string }

@app.post("/gpx", status_code=status.HTTP_200_OK)
def downloadGPX(item: AZGPXRequest, response: Response):

    print("Go go gadget GPX!")
    bounds = get_bounds(item)
    cutoff_alt = get_cutoff_alt(item)
    az_geo = get_gpx(item, bounds)

    print(f'Bounds: {bounds}')
    print(f'Cutoff Alt: {cutoff_alt}')
    print(f'AZ GPX Data: {az_geo}')

    print('v002')

    output_file = ''

    with tempfile.TemporaryDirectory() as tmpdirname:

        with open(tmpdirname + item.summit_ref + '.gpx', 'w') as fp:
            
            fp.write(az_geo)

            return {'az_gpx': az_geo}

    # Convert to string and remove altitude (0m)
    # az_geo_string = str(az_geo)

#    print("Polygon String: ", az_geo_string)
    
#    return {'az_gpx': az_geo}