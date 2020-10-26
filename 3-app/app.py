import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import xarray as xr
import plotly
import chart_studio.plotly as py
from plotly.graph_objs import *
import numpy as np           
from scipy.io import netcdf  
from mpl_toolkits.basemap import Basemap

f_path = 'total_precipitation_1979-01.nc'#your file from the NCEP reanalysis plotter

# Retrieve data from NetCDF file
with netcdf.netcdf_file(f_path, 'r') as f:
    lon = f.variables['longitude'][::]     # copy as list
    lat = f.variables['latitude'][::-1]    # invert the latitude vector -> South to North
    tp = f.variables['tp'][0,::-1,:]       # squeeze out the time dimension, 
                                           # invert latitude index

# Shift 'lon' from [0,360] to [-180,180], make numpy array
tmp_lon = np.array([lon[n]-360 if l>=180 else lon[n] 
                   for n,l in enumerate(lon)])  # => [0,180]U[-180,2.5]

i_east, = np.where(tmp_lon>=0)  # indices of east lon
i_west, = np.where(tmp_lon<0)   # indices of west lon
lon = np.hstack((tmp_lon[i_west], tmp_lon[i_east]))  # stack the 2 halves

# Correspondingly, shift the 'precip' array
tp_ground = np.array(tp)
tp = np.hstack((tp_ground[:,i_west], tp_ground[:,i_east]))
#tp = (1000/30)*tp
print(np.amax(tp))
print(np.amin(tp))

trace1 = Contour(
    z=(tp,
    x=lon,
    y=lat,
    colorscale= [[0.0, '#543005'], [0.07692307692307693, '#7f4909'], [0.15384615384615385, '#a76a1d'], [0.23076923076923078, '#c99545'], [0.3076923076923077, '#e1c582'], [0.38461538461538464, '#f2e2b8'], [0.46153846153846156, '#f6f0e2'], [0.5384615384615384, '#e4f1ef'], [0.6153846153846154, '#bce6e0'], [0.6923076923076923, '#86cfc4'], [0.7692307692307693, '#4ea79e'], [0.8461538461538461, '#218078'], [0.9230769230769231, '#015c53'], [1.0, '#003c30']],
    zauto=False,  # custom contour levels
    zmin=0,      # first contour level
    zmax=3,        # last contour level  => colorscale is centered about 0
    
colorbar= {
    "borderwidth": 0, 
    "outlinewidth": 0, 
    "thickness": 15, 
    "tickfont": {"size": 14}, 
    "title": "mm/day"}, #gives your legend some units                                                                     

contours= {
    "end": 2.5, 
    "showlines": False, 
    "size": 0.25, #this is your contour interval
    "start": 0}

)    
# Make shortcut to Basemap object, 
# not specifying projection type for this example
m = Basemap() 

# Make trace-generating function (return a Scatter object)
def make_scatter(x,y):
    return Scatter(
        x=x,
        y=y,
        mode='lines',
        line=Line(color="black"),
        name=' '  # no name on hover
    )

# Functions converting coastline/country polygons to lon/lat traces
def polygons_to_traces(poly_paths, N_poly):
    ''' 
    pos arg 1. (poly_paths): paths to polygons
    pos arg 2. (N_poly): number of polygon to convert
    '''
    # init. plotting list
    data = dict(
        x=[],
        y=[],
        mode='lines',
        line=Line(color="black"),
        name=' '
    )

    for i_poly in range(N_poly):
        poly_path = poly_paths[i_poly]
        
        # get the Basemap coordinates of each segment
        coords_cc = np.array(
            [(vertex[0],vertex[1]) 
             for (vertex,code) in poly_path.iter_segments(simplify=False)]
        )
        
        # convert coordinates to lon/lat by 'inverting' the Basemap projection
        lon_cc, lat_cc = m(coords_cc[:,0],coords_cc[:,1], inverse=True)
    
        
        # add plot.ly plotting options
        data['x'] = data['x'] + lon_cc.tolist() + [np.nan]
        data['y'] = data['y'] + lat_cc.tolist() + [np.nan]
        
        # traces.append(make_scatter(lon_cc,lat_cc))
     
    return [data]

# Function generating coastline lon/lat traces
def get_coastline_traces():
    poly_paths = m.drawcoastlines().get_paths() # coastline polygon paths
    N_poly = 91  # use only the 91st biggest coastlines (i.e. no rivers)
    return polygons_to_traces(poly_paths, N_poly)

# Function generating country lon/lat traces
def get_country_traces():
    poly_paths = m.drawcountries().get_paths() # country polygon paths
    N_poly = len(poly_paths)  # use all countries
    return polygons_to_traces(poly_paths, N_poly)

# Get list of of coastline, country, and state lon/lat traces
traces_cc = get_coastline_traces()+get_country_traces()
data = Data([trace1]+traces_cc)

title = u"Total precipitation<br>Jan 1979"

#anno_text = "Data courtesy of \
#<a href='http://www.esrl.noaa.gov/psd/data/composites/day/'>\
#NOAA Earth System Research Laboratory</a>"

axis_style = dict(
    zeroline=False,
    showline=False,
    showgrid=False,
    ticks='',
    showticklabels=False,
)

layout = Layout(
    title=title,
    showlegend=False,
    hovermode="closest",        # highlight closest point on hover
    xaxis=XAxis(
        axis_style,
        range=[lon[0],lon[-1]]  # restrict y-axis to range of lon
    ),
    yaxis=YAxis(
        axis_style,
    ),
#    annotations=Annotations([
#        Annotation(
#            text=anno_text,
#            xref='paper',
#            yref='paper',
#            x=0,
#            y=1,
#            yanchor='bottom',
#            showarrow=False
#        )
 #   ]),
    autosize=False,
    width=1200,
    height=800,
)
fig = Figure(data=data, layout=layout)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0')

#py.iplot(fig, filename="ERA5 total precipitation", width=1000)

 

