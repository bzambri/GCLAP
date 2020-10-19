def zonal_mean(dset):
    # Find mean temperature for each latitude
    mean_lat = dset.map(lambda x: x.mean(dim='longitude'))

    return mean_lat
