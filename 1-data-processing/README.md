# Data processing scripts

This directory contains the pySpark scripts that were used to read the reanalysis data from S3 and process and write the data to CockroachDB. They are:

#### `get_ERA5_pressure_levels.py` and `get_ERA5_single_levels.py`
These files download the 3- and 4-dimensional ERA5 reanalysis data, respectively, and upload the files to S3.

#### `writeTable.py`
 
