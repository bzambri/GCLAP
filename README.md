# Global Climate data Lake and Analysis Platform (GCLAP)

## Overview

As a climate scientist, every time I wanted to answer a new research question, I spent hour after hour looking for, downloading, and cleaning new data. According to a study by CrowdFlower (now Figure Eight), data scientists spend about 80% of their time preparing and managing data for analysis. According to the same study, 76% of data scientists view data preparation as the least enjoyablbe part of their work.

The Global Climate data Lake and Analysis Platform (GCLAP) is a climate data warehouse that takes care of the painful process of preparing and managing data. With its user interface, data scientists can simply choose the variable and the analysis that they want to perform, and GCLAP does the work, allowing near-instant download of visualizations or even the output, if the user wants to perform their own visualization using some other popular geophsycial data visualization tool (e.g., [NCL](https://ncl.ucar.edu)).

## Data

Monthly output from the European Centre for Medium-Range Weather Forecasts ([ECMWF](https://ecmwf.int)) ERA5 reanalysis product are available in [netcdf](https://www.unidata.ucar.edu/software/netcdf/) format through their API.

## Installation

Here is an overview of the steps required to setup the cluster:

1. Download the ERA5 reanalysis data to S3.
2. Set up a CockroachDB cluster.
3. Set up a Spark cluster for data processing.
4. Calculate desired tables using Spark and save to CockroachDB.
6. Set up a web server with Apache and UI with Plotly/Dash.
7. Set up Airflow to run the data pipeline and refresh the data and UI monthly.*

## Architecture

![Tech Stack](/images/stack.png)
