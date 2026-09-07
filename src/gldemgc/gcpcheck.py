import argparse
from collections import namedtuple, OrderedDict
import logging
import numpy as np
from osgeo import gdal, ogr, osr
from pathlib import Path
import sys
from tqdm import tqdm

gdal.UseExceptions()
ogr.UseExceptions()
osr.UseExceptions()

LOG_LEVELS = OrderedDict([
    ('DEBUG', logging.DEBUG),
    ('INFO', logging.INFO),
    ('WARNING', logging.WARNING),
    ('ERROR', logging.ERROR),
    ('CRITICAL', logging.CRITICAL)
])

DEM_Z_FIELD_NAME = 'dem_z'
GCP_Z_FIELD_NAME = 'gcp_z'
Z_DIFF_FIELD_NAME = 'z_diff'

class Dem:
    def __init__(self, path: Path):
        logging.info(f'Opening DEM dataset {path}...')
        self.dataset = gdal.Open(path, gdal.GA_ReadOnly)

    def get_z(self, x, y, srs=None):
        band = self.dataset.GetRasterBand(1)

        # If srs is None, will use the dataset's native srs
        z = band.InterpolateAtGeolocation(x, y, srs, gdal.GRIORA_Bilinear)

        return z

class Gcps:
    def __init__(self, path: Path, attribute_filter=None, z_field_name=None):
        logging.info(f'Opening GCP dataset {path}...')
        self.dataset = ogr.Open(path, gdal.GA_ReadOnly)
        self.layer = self.dataset.GetLayer()
        self.layer.SetAttributeFilter(attribute_filter)
        logging.debug(f"Using GCP attribute filter '{attribute_filter}'")
        self.z_field_name = z_field_name
        if self.z_field_name is None:
            logging.debug('GCP Z field name is None, will use geometry Z')
        else:
            logging.debug(f'Using field name "{self.z_field_name}" for GCP Z values')

    def get_points(self):
        points_list = []
        for feature in self.layer:
            geometry_ref = feature.GetGeometryRef()

            x = geometry_ref.GetX()
            y = geometry_ref.GetY()

            if self.z_field_name is None:
                if geometry_ref.Is3D():
                    z = geometry_ref.GetZ()
                else:
                    raise ValueError('no Z value available')
            else:
                z = feature.GetFieldAsDouble(self.z_field_name)

            points_list.append((x, y, z))

        points_array = np.array(points_list)
        return points_array

    def get_srs(self):
        return self.dataset.GetSpatialRef()

GcpResult = namedtuple('GcpResult', ['x', 'y', 'dem_z', 'gcp_z', 'z_diff'])

class OutputPoints:
    def __init__(self, path: Path, layer_name, srs):
        logging.info(f'Creating output dataset {path}...')
        driver = ogr.GetDriverByName('GPKG')
        self.geometry_type = ogr.wkbPoint
        self.dataset = driver.CreateDataSource(path)

        self.layer = self.dataset.CreateLayer(layer_name, srs, self.geometry_type)
        self.layer.CreateField(ogr.FieldDefn(DEM_Z_FIELD_NAME, ogr.OFTReal))
        self.layer.CreateField(ogr.FieldDefn(GCP_Z_FIELD_NAME, ogr.OFTReal))
        self.layer.CreateField(ogr.FieldDefn(Z_DIFF_FIELD_NAME, ogr.OFTReal))

    def add_point(self, gcp_result):
        # (x, y, z) = input_point
        feature = ogr.Feature(self.layer.GetLayerDefn())
        geometry = ogr.Geometry(self.geometry_type)
        geometry.AddPoint_2D(gcp_result.x, gcp_result.y)
        feature.SetGeometry(geometry)
        feature.SetField(DEM_Z_FIELD_NAME, gcp_result.dem_z)
        feature.SetField(GCP_Z_FIELD_NAME, gcp_result.gcp_z)
        feature.SetField(Z_DIFF_FIELD_NAME, gcp_result.z_diff)
        self.layer.CreateFeature(feature)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('dem', type=str, help='path to DEM raster')
    parser.add_argument('gcps', type=str, help='path to GCP data')
    parser.add_argument('output', type=str, help='desired path to output (GPKG)')
    # parser.add_argument('--geoid', type=str, help='path to geoid') # TODO
    parser.add_argument('--gcp-z-field', type=str, help='name of Z field in GCP features')
    parser.add_argument('--gcp-attribute-filter', type=str, help='SQL WHERE-style attribute filter for GCPs')
    parser.add_argument('--progress', action='store_true', help='show progress bar during processing')
    parser.add_argument('--log-level', type=str, choices=LOG_LEVELS.keys(), default='WARNING', help='logging level')
    parsed_args = parser.parse_args(args)
    return parsed_args

def main():
    input_args = parse_args(sys.argv[1:])

    logging.basicConfig(level=LOG_LEVELS[input_args.log_level])

    dem_path = Path(input_args.dem)
    gcps_path = Path(input_args.gcps)
    output_path = Path(input_args.output)
    # if input_args.geoid is not None:
    #     geoid_path = Path(input_args.geoid)
    gcp_z_field_name = input_args.gcp_z_field
    gcp_attribute_filter = input_args.gcp_attribute_filter

    dem = Dem(dem_path)
    gcps = Gcps(gcps_path, attribute_filter=gcp_attribute_filter, z_field_name=gcp_z_field_name)
    output_points = OutputPoints(output_path, 'gcp_results', gcps.get_srs())

    gcp_points = gcps.get_points()

    gcp_iterator = gcp_points
    if input_args.progress:
        gcp_iterator = tqdm(gcp_iterator, unit='GCP', ascii=True)

    for gcp_point in gcp_iterator:
        (x, y, gcp_z) = gcp_point
        dem_z = dem.get_z(x, y, gcps.get_srs())
        z_diff = dem_z - gcp_z

        gcp_result = GcpResult(x=x, y=y, dem_z=dem_z, gcp_z=gcp_z, z_diff=z_diff)

        output_points.add_point(gcp_result)
