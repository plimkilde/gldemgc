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

class Gca:
    def __init__(self, path: Path):
        self.dataset = gdal.open(path, gdal.GA_ReadOnly)

    def get_cross_corr(self, dem: gdal.Dataset):
        #dem_band = dem.GetRasterBand(1)
        pass

def parse_args(args):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--progress', action='store_true', help='show progress bar during processing')
    parser.add_argument('--log-level', type=str, choices=LOG_LEVELS.keys(), default='WARNING', help='logging level')
    parsed_args = parser.parse_args(args)
    return parsed_args

def main():
    input_args = parse_args(sys.argv[1:])

    logging.basicConfig(level=LOG_LEVELS[input_args.log_level])


