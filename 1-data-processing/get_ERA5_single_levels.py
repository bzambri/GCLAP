#Script to get the ERA5 near-surface output from the Copernicus Climate Data Store

import cdsapi
import os

#the variables we want to download
var_list = ['10m_u_component_of_wind', '10m_v_component_of_wind','sea_surface_temperature', 'significant_height_of_combined_wind_waves_and_swell',
            'surface_pressure', 'total_precipitation']

c = cdsapi.Client()
for var in var_list:
    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': [
                var,
            ],
            'year': [
                '1979', '1980', '1981',
                '1982', '1983', '1984',
                '1985', '1986', '1987',
                '1988', '1989', '1990',
                '1991', '1992', '1993',
                '1994', '1995', '1996',
                '1997', '1998', '1999',
                '2000', '2001', '2002',
                '2003', '2004', '2005',
                '2006', '2007', '2008',
                '2009', '2010', '2011',
                '2012', '2013', '2014',
                '2015', '2016', '2017',
                '2018', '2019', '2020',
            ],
            'month': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
            ],
            'time': '00:00',
            'format': 'netcdf',
        },
        f'{var}.nc')

    #divide the output into monthly files and write to S3    
    i=0
    for yr in range(1979,2020):
        for mon in range(1,13):
            #filename
            outfile = f'{var}_{yr}-{mon:02d}.nc'
            #get the single month
            os.system(f'ncea -d time,{i},{i} {var}.nc {outfile}')
            #write to S3
            os.system(f'aws s3 mv {outfile} s3://reanalysis-folders/ERA5/single-levels/{var}/')
            i = i+1
    #once we have written all the months, we can get rid of the local file        
    os.system(f'rm {var}.nc')
