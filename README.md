# gldemgc
GCP and GCA utility for Greenland DEM

## Installation
To use the software, ensure you have [Pixi](https://pixi.prefix.dev/)
installed.

## Usage
### GCP check
The utility `gcpcheck` will find the discrepancies between a provided DEM
raster and a collection of ground control points (GCPs). It outputs a
GeoPackage (GPKG) file containing results for each GCP.

```
usage: pixi run gcpcheck [-h] [--gcp-z-field GCP_Z_FIELD]
                         [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         dem gcps output

positional arguments:
  dem                   path to DEM raster
  gcps                  path to GCP data
  output                desired path to output (GPKG)

options:
  -h, --help            show this help message and exit
  --gcp-z-field GCP_Z_FIELD
                        name of Z field in GCP features
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        logging level
```

The output file will contain 2D points in the same SRS as the GCP input. Each
point will have the following fields:

| Field    | Description |
| -------- | ----------- |
| `dem_z`  | Z value of the raster DEM, point-sampled at the GCP location (using bilinear interpolation) |
| `gcp_z`  | GCP Z value |
| `z_diff` | Difference between DEM and GCP (`dem_z` - `gcp_z`) |

### GCA check
TODO
