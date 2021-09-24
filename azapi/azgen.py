import tempfile
from os import path
from typing import Tuple

import elevation
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import numpy as np

from descartes import PolygonPatch
import alphashape

from .models import AZRequest


def get_bounds(request: AZRequest) -> Tuple[float, float, float, float]:
    # Generate the extent
    summit_lat_min = float('{:.8f}'.format(request.summit_lat - request.deg_delta))
    summit_lat_max = float('{:.8f}'.format(request.summit_lat + request.deg_delta))
    summit_long_min = float('{:.8f}'.format(request.summit_long - request.deg_delta))
    summit_long_max = float('{:.8f}'.format(request.summit_long + request.deg_delta))

    return summit_long_min, summit_lat_min, summit_long_max, summit_lat_max


def get_cutoff_alt(request: AZRequest) -> float:
    return request.summit_alt - request.sota_summit_alt_thres


# clip -o data/{summit_ref}-30m-DEM.tif --bounds {summit_long_min} {summit_lat_min} {summit_long_max} {summit_lat_max}
def get_az(request: AZRequest, bounds: Tuple[float, float, float, float]) -> np.ndarray:

    # Generate the extent
    summit_lat_min = float('{:.8f}'.format(request.summit_lat - request.deg_delta))
    summit_lat_max = float('{:.8f}'.format(request.summit_lat + request.deg_delta))
    summit_long_min = float('{:.8f}'.format(request.summit_long - request.deg_delta))
    summit_long_max = float('{:.8f}'.format(request.summit_long + request.deg_delta))

    # Set SOTA Altitude AZ (Activation Zone) Cutoff
    summit_alt_az_min = request.summit_alt - request.sota_summit_alt_thres

    # Download DEM and Calculate Activation Zone

    # Python will clean up this temp directory once out of scope or garbage collected
    with tempfile.TemporaryDirectory() as tmpdir:
        # Get clipped elevation data
        clip_file = path.join(tmpdir, "elevation_clip_data")
        elevation.clip(bounds=bounds, output=clip_file)

        # Use gdal to parse the data
        gdal_data = gdal.Open(clip_file)
        gdal_band = gdal_data.GetRasterBand(1)
        nodataval = gdal_band.GetNoDataValue()

        # convert to a numpy array
        dem = gdal_data.ReadAsArray().astype(np.float)

        # replace missing values if necessary
        if np.any(dem == nodataval):
            dem[dem == nodataval] = np.nan
        
        # Calculate Activation Zone Altitude Mask (all data points at or above alt cutoff)
        num_x, num_y = dem.shape

        center_x = int(num_x/2)
        center_y = int(num_y/2)

        az_mask = np.zeros((num_x, num_y))

        # If the requested summit altitude is too high, use the DEM altitude as the summit altitude
        if ( request.summit_alt - dem[center_x,center_y] > request.sota_summit_alt_thres - 1 ):
            print("REQUEST ALT: ", request.summit_alt)
            print("DEM ALT: ", dem[center_x,center_y])
            summit_alt_az_min = dem[center_x,center_y] - request.sota_summit_alt_thres

        for x in range(num_x):
            for y in range(num_y):
                if dem[x,y] >= summit_alt_az_min:
                    az_mask[x,y] = 1

        # Filter data points that are both within the 
        # activation zone altitude and are connected to the summit
        az_mask_s = np.zeros((num_x, num_y))
        az_mask_s[center_x,center_y] = 2 

        az = np.zeros((num_x, num_y))

        # Start at the summit (center) and expand outward until outside the AZ
        #    0 = Unassigned or outside of AZ
        #    1 = Within AZ
        #    2 = Marked for searching
        while 2 in az_mask_s:
            for x in range(num_x):
                for y in range(num_y):
                    if az_mask_s[x,y] == 2 and az_mask[x,y] == 1:
                        
                        if az_mask_s[x+1,y+1] == 0 and az_mask[x+1,y+1] == 1:
                            az_mask_s[x+1,y+1] = 2
                        
                        if az_mask_s[x+1,y-1] == 0 and az_mask[x+1,y-1] == 1:
                            az_mask_s[x+1,y-1] = 2
                        
                        if az_mask_s[x-1,y+1] == 0 and az_mask[x-1,y+1] == 1:
                            az_mask_s[x-1,y+1] = 2
                            
                        if az_mask_s[x-1,y-1] == 0 and az_mask[x-1,y-1] == 1:
                            az_mask_s[x-1,y-1] = 2

                        if az_mask_s[x+1,y] == 0 and az_mask[x+1,y] == 1:
                            az_mask_s[x+1,y] = 2
                        
                        if az_mask_s[x-1,y] == 0 and az_mask[x-1,y-1] == 1:
                            az_mask_s[x-1,y] = 2
                        
                        if az_mask_s[x,y+1] == 0 and az_mask[x,y+1] == 1:
                            az_mask_s[x,y+1] = 2
                        
                        if az_mask_s[x,y-1] == 0 and az_mask[x,y-1] == 1:
                            az_mask_s[x,y-1] = 2

                    if az_mask_s[x,y] == 2:
                        az_mask_s[x,y] = 1

        # The following is meant for future use. Copying az_mask_s directly to az works just as well.
        for x in range(num_x):
            for y in range(num_y):
                if az_mask_s[x,y] == 1:
                    az[x,y] = 1

        # Generate Latitude and Longitude array (shares indices with az)
        # Calculate lat/long step per index
        az_lat_step = (summit_lat_max-summit_lat_min)/num_y
        az_long_step = (summit_long_max-summit_long_min)/num_x

        lat = np.zeros((num_x, num_y))
        long = np.zeros((num_x, num_y))

        # Calculate Lat/Long array
        for x in range(num_x):
            for y in range(num_y):
                lat[x,y] = summit_lat_max - (az_lat_step*x)
                long[x,y] = summit_long_min + (az_long_step*y)

        # Print all AZ data points
        # for x in range(num_x):
        #     for y in range(num_y):
        #         if az[x,y] == 1:
        #             print("Lat: ", lat[x,y], "Long: ", long[x,y], "Alt: ", dem[x,y])

        # Configure spatial reference
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)

        # Collect all Geometry
        geomcol = []

        # Add all lat/long points to generate a AZ polygon using convexhull
        for x in range(num_x):
            for y in range(num_y):
                if az[x,y] == 1:

                    # Add each AZ point
                    geomcol.append( (float(long[x,y]), float(lat[x,y])) )
        
        # AZ Polygon Geometry using Concave Hull
        azgeo = alphashape.alphashape(geomcol, 4000.0)
        
        # Return AZ polygon
        return azgeo
