import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import xarray as xr
import plotly
import chart_studio.plotly as py
from plotly.graph_objs import *
import plotly.graph_objects as go
import numpy as np           
from scipy.io import netcdf  
from mpl_toolkits.basemap import Basemap

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

end = {"u10":3,"v10":3,"d2m":3,"t2m":3,"msl":500,"sst":2,"sp":500,"tp":10}
interval = {"u10":0.5,"v10":0.5,"d2m":0.5,"t2m":0.5,"msl":100,"sst":0.25,"sp":100,"tp":1}
units = {"u10":"m/s","v10":"m/s","d2m":"K","t2m":"K","msl":"Pa","sst":"K","sp":"Pa","tp":"mm"}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

f_path = 'single-level.nc' #your file from the NCEP reanalysis plotter
#f_path = 'compday.uD1lrjCi2B.nc'

# Retrieve data from NetCDF file
f = netcdf.netcdf_file(f_path, 'r')
    
lon = f.variables['longitude'][::]    # copy as list
lat = f.variables['latitude'][::-1]    # invert the latitude vector -> South to North
time = f.variables['time'][::]

months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December", "Annual"]

# Shift 'lon' from [0,360] to [-180,180], make numpy array
tmp_lon = np.array([lon[n]-360 if l>=180 else lon[n] 
                   for n,l in enumerate(lon)])  # => [0,180]U[-180,2.5]

i_east, = np.where(tmp_lon>=0)  # indices of east lon
i_west, = np.where(tmp_lon<0)   # indices of west lon
lon = np.hstack((tmp_lon[i_west], tmp_lon[i_east]))  # stack the 2 halves

#pop the dimension variables
f.variables.pop('longitude')
f.variables.pop('latitude')
f.variables.pop('time')

#get what's left over
available_indicators = f.variables.keys()

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


#app.layout = html.Div(children=[
#    html.H1(children='Global Climate data Lake and Analysis Platform (GCLAP)'),

#    dcc.Graph(
#        id='map',
#        figure=fig
#    )
#])
app.layout = html.Div([html.H1(children='Global Climate data Lake and Analysis Platform (GCLAP)'),
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='variable',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='t2m'
            )
        ],
        style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='month',
                options=[{'label': months[i], 'value': i} for i in range(len(months))],
                value=0
            )
        ],
        style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='year1',
                options=[{'label': i, 'value': i} for i in range(1979,2020)],
                value=1979
            )
        ],
        style={'width': '10%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='year2',
                options=[{'label': i, 'value': i} for i in range(1979,2020)],
                value=1979
            )
        ],
        style={'width': '10%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='year3',
                options=[{'label': i, 'value': i} for i in range(1979,2020)],
                value=1979
            )
        ],
        style={'width': '10%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='year4',
                options=[{'label': i, 'value': i} for i in range(1979,2020)],
                value=1979
            )
        ],
        style={'width': '10%', 'display': 'inline-block'})

    ]),

    dcc.Graph(id='indicator-graphic')
])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('variable', 'value'),
     Input('month', 'value'),
     Input('year1', 'value'),
     Input('year2', 'value'),
     Input('year3', 'value'),
     Input('year4', 'value')])

def update_graph(variable, month, year1, year2, year3, year4):

    #get the right units
    scale_factor = f.variables[variable].scale_factor
    add_offset = f.variables[variable].add_offset

    #monthly analysis
#    if month != 12:
    ts = f.variables[variable][12*(year1-1979)+month:12*(year2-1979)+month:12,::-1,:]
    clim = f.variables[variable][12*(year3-1979)+month:12*(year4-1979)+month:12,::-1,:] #get the monthly climatology
    #annual average
#    else:
#        ts = f.variables[variable][12*(year1-1979):12*(end_year-1979),::-1,:]
#        clim = f.variables[variable][:,::-1,:] #get the monthly climatology    

    # Take the time-mean and shift the variable array
    ts_ground = np.mean(np.array(ts)*scale_factor + add_offset,axis=0)
    ts_clim   = np.mean(np.array(clim)*scale_factor + add_offset,axis=0)
    ts_ground = ts_ground - ts_clim
    ts        = np.hstack((ts_ground[:,i_west], ts_ground[:,i_east]))

    #convert precipitation to mm/day
    if variable == 'tp':
        ts = 1000*ts
        scale = [[0.0, '#543005'], [0.07692307692307693, '#7f4909'], [0.15384615384615385, '#a76a1d'], [0.23076923076923078, '#c99545'], [0.3076923076923077, '#e1c582'], [0.38461538461538464, '#f2e2b8'], [0.46153846153846156, '#f6f0e2'], [0.5384615384615384, '#e4f1ef'], [0.6153846153846154, '#bce6e0'], [0.6923076923076923, '#86cfc4'], [0.7692307692307693, '#4ea79e'], [0.8461538461538461, '#218078'], [0.9230769230769231, '#015c53'], [1.0, '#003c30']]
    else:
        scale = [[0.0, '#171c42'], [0.07692307692307693, '#263583'], [0.15384615384615385, '#1a58af'], [0.23076923076923078, '#1a7ebd'], [0.3076923076923077, '#619fbc'], [0.38461538461538464, '#9ebdc8'], [0.46153846153846156, '#d2d8dc'], [0.5384615384615384, '#e6d2cf'], [0.6153846153846154, '#daa998'], [0.6923076923076923, '#cc7b60'], [0.7692307692307693, '#b94d36'], [0.8461538461538461, '#9d2127'], [0.9230769230769231, '#6e0e24'], [1.0, '#3c0911']]

    trace1 = Contour(
    z=ts,
    x=lon,
    y=lat,
    colorscale = scale,
    zauto=False,  # custom contour levels
    zmin=-1*end[variable],      # first contour level
    zmax=end[variable],        # last contour level  => colorscale is centered about 0
    
    colorbar= {
        "borderwidth": 0, 
        "outlinewidth": 0, 
        "thickness": 15, 
        "tickfont": {"size": 14}, 
        "title": units[variable]}, #gives your legend some units                                                                     

    contours= {
        "end": end[variable],
        "showlines": False, 
        "size": interval[variable], #this is your contour interval
        "start": -1*end[variable]}

    )
    data = Data([trace1]+traces_cc)
    title = f"{months[month]} {variable} anomaly, {year1}-{year2} minus {year3}-{year4}"

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
        autosize=False,
        width=1200,
        height=800,
    )
    fig = Figure(data=data, layout=layout)

    #fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
    #                 y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
    #                 hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    #fig.update_xaxes(title=xaxis_column_name, 
    #                 type='linear' if xaxis_type == 'Linear' else 'log') 

    #fig.update_yaxes(title=yaxis_column_name, 
    #                 type='linear' if yaxis_type == 'Linear' else 'log') 

    return fig

#fig = go.Figure(layout = go.Layout(
#    title=title,
#    showlegend=False,
#    hovermode="closest",        # highlight closest point on hover
#    xaxis=XAxis(
#        axis_style,
#        range=[lon[0],lon[-1]]  # restrict y-axis to range of lon
#    ),
#    yaxis=YAxis(
#        axis_style,
#    ),
#    autosize=False,
#    width=1200,
#    height=800,
#))

#fig.add_trace(trace1)
#fig.add_trace(trace4)
#fig.add_trace(trace7)
#fig.add_trace(trace10)

"""
# Add Buttons
#fig.update_layout(
    updatemenus=[
        dict(
            type="dropdown",
            direction="down",
            active=0,
            x=0.57,
            y=1.2,
            buttons=list([
                dict(label="DJF 2019",
                     method="update",
                     args=[{"visible": [True, False, False, False, True, True]},
                           {"title": "2m temperature anomaly, DJF 2019",
                            "annotations": []}]),
                dict(label="MAM 2019",
                     method="update",
                     args=[{"visible": [False, True, False, False, True, True]},
                           {"title": "2m temperature anomaly, MAM 2019",
                            "annotations": []}]),
                dict(label="JJA 2019",
                     method="update",
                     args=[{"visible": [False, False, True,  False, True, True]},
                           {"title": "2m temperature anomaly, JJA 2019",
                            "annotations": []}]),
                dict(label="SON 2019",
                     method="update",
                     args=[{"visible": [False, False, False, True, True, True]},
                           {"title": "2m temperature anomaly, SON 2019",
                            "annotations": []}]),
            ]),
        )
    ])
"""
#outward-facing dashboard
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0')

 

