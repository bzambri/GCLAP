def zonal_mean(dset):

    # Find zonal mean for each latitude
    mean_lat = dset.map(lambda x: x.mean(dim='longitude'))

    return mean_lat
