#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2022 Activation.zone
# File: azapi/azgen.py

import tempfile
from os import path
from typing import Tuple

import elevation
import shapely
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import numpy as np
import alphashape
from shapely.geometry import Point

from .models import AZRequest


def get_bounds(request: AZRequest) -> Tuple[float, float, float, float]:
    # Generate the extent
    summit_lat_min = float("{:.8f}".format(request.summit_lat - request.deg_delta))
    summit_lat_max = float("{:.8f}".format(request.summit_lat + request.deg_delta))
    summit_long_min = float("{:.8f}".format(request.summit_long - request.deg_delta))
    summit_long_max = float("{:.8f}".format(request.summit_long + request.deg_delta))

    return summit_long_min, summit_lat_min, summit_long_max, summit_lat_max


def get_single_polygon(request: AZRequest, azgeo: shapely.Polygon) -> shapely.Polygon:
    summit_point = Point(float(request.summit_long), float(request.summit_lat))
    if hasattr(azgeo, "geoms"):  # MultiPolygon
        containing = None
        for poly in azgeo.geoms:
            if poly.covers(summit_point):
                containing = poly
                break
        if containing is None:
            containing = min(azgeo.geoms, key=lambda p: p.distance(summit_point))
        return containing
    return azgeo


def get_cutoff_alt(request: AZRequest) -> float:
    return request.summit_alt - request.sota_summit_alt_thres


# clip -o data/{summit_ref}-30m-DEM.tif --bounds {summit_long_min} {summit_lat_min} {summit_long_max} {summit_lat_max}
def get_az(request: AZRequest, bounds: Tuple[float, float, float, float]) -> shapely.Polygon:

    # Generate the extent
    summit_long_min, summit_lat_min, summit_long_max, summit_lat_max = bounds

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
        nodata_val = gdal_band.GetNoDataValue()

        # convert to a numpy array
        dem = gdal_data.ReadAsArray().astype(np.float64)

        # replace missing values if necessary
        if np.any(dem == nodata_val):
            dem[dem == nodata_val] = np.nan

        # Calculate Activation Zone Altitude Mask (all data points at or above alt cutoff)
        num_x, num_y = dem.shape

        center_x = int(num_x / 2)
        center_y = int(num_y / 2)

        az_mask = np.zeros((num_x, num_y))

        # If the requested summit altitude is too high, use the DEM altitude as the summit altitude
        if request.summit_alt - dem[center_x, center_y] > request.sota_summit_alt_thres - 1:
            print("REQUEST ALT: ", request.summit_alt)
            print("DEM ALT: ", dem[center_x, center_y])
            summit_alt_az_min = dem[center_x, center_y] - request.sota_summit_alt_thres

        for x in range(num_x):
            for y in range(num_y):
                if dem[x, y] >= summit_alt_az_min:
                    az_mask[x, y] = 1

        # Filter data points that are both within the
        # activation zone altitude and are connected to the summit
        az_mask_s = np.zeros((num_x, num_y))
        az_mask_s[center_x, center_y] = 2
        az_mask_s_padded = np.pad(az_mask_s, 1, mode="constant", constant_values=0)
        az_mask_padded = np.pad(az_mask, 1, mode="constant", constant_values=0)

        rows, cols = az_mask_s_padded.shape

        az = np.zeros((num_x, num_y))

        # Start at the summit (center) and expand outward until outside the AZ
        #    0 = Unassigned or outside of AZ
        #    1 = Within AZ
        #    2 = Marked for searching
        while 2 in az_mask_s_padded:
            # Only iterate internal cells
            for x in range(1, rows - 1):
                for y in range(1, cols - 1):
                    if az_mask_s_padded[x, y] == 2 and az_mask_padded[x, y] == 1:
                        # Check 8 neighbors
                        neighbors = [
                            (1, 1),
                            (1, -1),
                            (-1, 1),
                            (-1, -1),
                            (1, 0),
                            (-1, 0),
                            (0, 1),
                            (0, -1),
                        ]
                        for dx, dy in neighbors:
                            if az_mask_s_padded[x + dx, y + dy] == 0 and az_mask_padded[x + dx, y + dy] == 1:
                                az_mask_s_padded[x + dx, y + dy] = 2
                    if az_mask_s_padded[x, y] == 2:
                        az_mask_s_padded[x, y] = 1

            # Remove padding
        az_mask_s = az_mask_s_padded[1:-1, 1:-1]

        # Copy to final AZ mask
        az[az_mask_s == 1] = 1

        # Generate Latitude and Longitude array (shares indices with az)
        # Calculate lat/long step per index
        az_lat_step = (summit_lat_max - summit_lat_min) / num_y
        az_long_step = (summit_long_max - summit_long_min) / num_x

        lat = np.zeros((num_x, num_y))
        long = np.zeros((num_x, num_y))

        # Calculate Lat/Long array
        for x in range(num_x):
            for y in range(num_y):
                lat[x, y] = summit_lat_max - (az_lat_step * x)
                long[x, y] = summit_long_min + (az_long_step * y)

        geom_col = [
            (float(long[x, y]), float(lat[x, y])) for x in range(num_x) for y in range(num_y) if az[x, y] == 1
        ]

        azgeo = alphashape.alphashape(geom_col, 4000.0)
        # If alphashape returns MultiPolygon, select the component that contains the summit
        azgeo = get_single_polygon(request, azgeo)

        # Return AZ polygon
        return azgeo


def get_gpx(request: AZRequest, bounds: Tuple[float, float, float, float], tmpdir: str) -> str:

    azgeo = get_az(request, bounds)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    driver = ogr.GetDriverByName("GPX")

    # Remove the output shapefile if it already exists
    if path.exists(tmpdir + request.summit_ref + ".gpx"):
        driver.DeleteDataSource(tmpdir + request.summit_ref + ".gpx")

    out = driver.CreateDataSource(tmpdir + request.summit_ref + ".gpx")

    # layer creation: if you use 'track_points', points are accepted
    o_l = out.CreateLayer("track_points", srs, ogr.wkbPoint)

    o_lat, o_long = azgeo.exterior.coords.xy

    # Add all lat/long points of AZ
    for x, y in zip(o_lat, o_long):
        # create point
        p = ogr.Geometry(ogr.wkbPoint)
        # initialize point with coordinates
        p.AddPoint(x, y)

        # prepare new "feature" using the layer's "feature definition",
        # initialize it by setting geometry and necessary field values
        feature_defn = o_l.GetLayerDefn()
        o_f = ogr.Feature(feature_defn)
        o_f.SetGeometry(p)
        o_f.SetField("track_fid", "1")
        o_f.SetField("track_seg_id", "1")

        # adapt this according to the timestamp format of your data source
        o_l.CreateFeature(o_f)

    return tmpdir + request.summit_ref + ".gpx"
