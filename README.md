# gldemgc
GCP and GCA utility for Greenland DEM

## Installation
To use the software, ensure you have [Pixi](https://pixi.prefix.dev/)
installed.

## Usage
### GCP check
The utility `gcpcheck` will find the discrepancies between a provided DEM
raster and a collection of ground control points (GCPs), optionally with a
user-provided geoid undulation applied. It outputs a GeoPackage (GPKG) file
containing results for each GCP.

```
usage: pixi run gcpcheck [-h] [--geoid GEOID] [--gcp-z-field GCP_Z_FIELD]
                         [--gcp-attribute-filter GCP_ATTRIBUTE_FILTER]
                         [--progress]
                         [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         dem gcps output

positional arguments:
  dem                   path to DEM raster
  gcps                  path to GCP data
  output                desired path to output (GPKG)

options:
  -h, --help            show this help message and exit
  --geoid GEOID         path to geoid raster
  --gcp-z-field GCP_Z_FIELD
                        name of Z field in GCP features
  --gcp-attribute-filter GCP_ATTRIBUTE_FILTER
                        SQL WHERE-style attribute filter for GCPs
  --progress            show progress bar during processing
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        logging level
```

The `--geoid` argument is optional. If not provided, the program will behave
as if the geoid undulation is zero everywhere.

The Z value for each GCP is extracted from the field specified with
`--gcp-z-field`. If not provided, the program will try to use the geometry Z
of the GCPs.

Note that `--gcp-attribute-filter` arguments may need careful escaping. For
example, to apply `source = "foo"` on Windows CMD, use
`--gcp-attribute-filter "source = \"foo\""`.

The output file will contain 2D points in the same SRS as the GCP input. Each
point will have the following fields:

| Field     | Description |
| --------- | ----------- |
| `dem_z`   | Z value of the raster DEM, point-sampled at the GCP location (using bilinear interpolation) |
| `geoid_z` | Z value of the geoid raster, point-sampled at the GCP location (using bilinear interpolation) |
| `gcp_z`   | GCP Z value |
| `z_diff`  | Difference between DEM and GCP (`dem_z` - (`gcp_z` - `geoid_z`)) |

The following example takes the file `dem.vrt` as the input DEM to check. For its GCP database, it uses the file `gcps.gpkg`, which is filtered by `source = "myfriends"`, and their Z value is taken from the field `height`. The geoidal undulation to use is provided in geoid.tif. Output is written to the file `results.gpkg`:
```
pixi run gcpcheck dem.vrt gcps.gpkg results.gpkg --geoid geoid.tif --gcp-z-field height --gcp-attribute-filter "source = \"myfriends\""
```

### GCA check
TODO
