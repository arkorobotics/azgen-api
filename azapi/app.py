from fastapi import FastAPI, Response, status

from fastapi.middleware.cors import CORSMiddleware

from .models import AZRequest, AZResponse
from .azgen import get_bounds, get_cutoff_alt, get_az
from .verison import __version__


app = FastAPI()

origins = ["*"]

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
    az_geo_string = az_geo_string.replace(" 0", "")

    print("Polygon String: ", az_geo_string)
    
    return { "az": az_geo_string }
