# Data processing scripts

This directory contains the pySpark scripts that were used to read the reanalysis data from S3 and process and write the data to CockroachDB.

`get_ERA5_pressure_levels.py` and `get_ERA5_single_levels.py` download the 2- and 3-dimensional ERA5 reanalysis data, respectively, and upload the files to S3.

`writeTable.py` is the function used to write the data to CockroachDB.

`write_single_levels.py` writes the raw monthly surface data (2-d; lat, lon) to CockroachDB.

`write_zonal_means.py` writes the zonal means of the 3-d (lat, lon, lev) data to CockroachDB.

`zonal_mean.py` calculates the zonal mean of the input. It is used in `write_zonal_means.py`.

Missing files: EOF
