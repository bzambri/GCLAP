def eof(dset,neof):

    # Find zonal mean for each latitude
    mean_lat = dset.map(lambda x: x.mean(dim='longitude'))


    return pattern, timeseries
