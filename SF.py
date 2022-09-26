#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 13:30:58 2022

@author: sahanaroy
"""
import pandas as pd
import geopandas as gpd
import requests

#data = requests.get('https://data.sfgov.org/api/geospatial/p5b7-5n3h?method=export&format=GeoJSON')
#gdf = gpd.GeoDataFrame(data.json())
#gdf.head()

nbd_full = gpd.read_file('https://data.sfgov.org/api/geospatial/p5b7-5n3h?method=export&format=GeoJSON')
nbd = nbd_full[["nhood", "geometry"]].set_index("nhood")
nbd = nbd.sort_values('nhood')
nbd.head()

df = pd.read_csv("https://data.sfgov.org/api/views/wg3w-h783/rows.csv?accessType=DOWNLOAD&bom=true&format=true")
list(df.columns)
df1 = pd.DataFrame(df,
                   columns=['Incident Time',
                            'Incident Year',
                            'Incident Day of Week',
                            'Incident Category',
                            'Incident Subcategory',
                            'Police District',
                            'Analysis Neighborhood',
                            'Latitude',
                            'Longitude',
                            'Point'])  # remove unneeded columns

df2 = df1.groupby(['Analysis Neighborhood','Incident Year']).count()
df2 = pd.DataFrame(df2,columns=['Incident Subcategory'])
df2.reset_index(inplace=True)   # default index, otherwise groupby column becomes index
df2.rename(columns={'Analysis Neighborhood':'nhood','Incident Subcategory':'count'}, inplace=True)
df2.sort_values(by='nhood', inplace=True, ascending=True)
list(df2.columns)

final_df = nbd.merge(df2, on = "nhood")
final_df.head()

import folium
from folium import plugins
# San Francisco latitude and longitude values
latitude = 37.77
longitude = -122.42

#The first 5000 data can now be displayed.
limit=5000
df1=df1.iloc[0:limit,:]#With iloc, the first 5000 items of data can be retrieved, and df1 has been updated.

df1=df1.dropna(subset=['Longitude'])
df1=df1.dropna(subset=['Latitude'])

m = folium.Map(location=[latitude,longitude],zoom_start=12)

incidents=plugins.MarkerCluster().add_to(m)  #Marking Cluster Objects for Data Events
type(incidents)

#Put data into the cluster object above
for lat,lng,label, in zip(df1['Latitude'],df1['Longitude'],df1['Incident Subcategory']):
    folium.Marker(
    location=[lat,lng],
    icon=None,
    popup=label,
    ).add_to(incidents)

m.save('SanFran.html')    

#df1.apply(lambda row:folium.CircleMarker(location=[row["Latitude"], row["Longitude"]]).add_to(m), axis=1)

from folium import plugins
from folium.plugins import MarkerCluster
# convert to (n, 2) nd-array format for heatmap
dfmatrix = df1[['Latitude', 'Longitude']].values
# plot heatmap
m.add_child(plugins.HeatMap(dfmatrix, radius=15))
folium.LayerControl(collapsed=False).add_to(m)
m.save('SanFran.html')

m2 = folium.Map(location=[latitude,longitude],zoom_start=12)

#top 10
Year_2022 = final_df[final_df['Incident Year']==2022]
Year_2021 = final_df[final_df['Incident Year']==2021]
Year_2020 = final_df[final_df['Incident Year']==2020]
Year_2019 = final_df[final_df['Incident Year']==2019]
Year_2018 = final_df[final_df['Incident Year']==2018]


# feature groups
feature_group0 = folium.FeatureGroup(name='2022', overlay=True, control=True, show=True).add_to(m2)
feature_group1= folium.FeatureGroup(name='2021', overlay=True, control=True, show=True).add_to(m2)
feature_group2 = folium.FeatureGroup(name='2020', overlay=True, control=True, show=True).add_to(m2)
feature_group3= folium.FeatureGroup(name='2019', overlay=True, control=True, show=True).add_to(m2)
feature_group4 = folium.FeatureGroup(name='2018', overlay=True, control=True, show=True).add_to(m2)


fs = [feature_group0,feature_group1,feature_group2,feature_group3,feature_group4]
years = [Year_2022,Year_2021,Year_2020,Year_2019,Year_2018]
for i in range(len(years)): 
    chloropeth1 = folium.Choropleth(
    geo_data=final_df,
    name='Years',
    data=years[i],
    columns=['nhood', 'count'],
    key_on='feature.properties.nhood',
    fill_color='YlOrRd',
    nan_fill_color="black",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Crime Rate in San Francisco',
    highlight=True,
    line_color='black').geojson.add_to(fs[i])

#geojson for labels
geojson1 = folium.GeoJson(data=final_df,
           name='San Francisco',
                     smooth_factor=2,
           style_function=lambda x: {'color':'black','fillColor':'transparent','weight':0.5},
            tooltip=folium.GeoJsonTooltip(fields=['nhood'],
                                          labels=False,
                                          sticky=True),
        highlight_function=lambda x: {'weight':3,'fillColor':'grey'},
            ).add_to(chloropeth1)

#from branca.colormap import linear  
#colormap = linear.YlGn_09.scale(
#final_df.count.min(),
#final_df.count.max()).to_step(10)
#colormap.caption = 'No. of Incidents'
#colormap.add_to(m2)    

folium.LayerControl(collapsed=False).add_to(m2)
m2.save('SanFran1.html')
                    
                   
# Add hover functionality.
style_function = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.50, 
                                'weight': 0.1}
NIL = folium.features.GeoJson(
    data = final_df,
    style_function=style_function, 
    control=False,
    highlight_function=highlight_function, 
    tooltip=folium.features.GeoJsonTooltip(
        fields=['nhood','count'],
        aliases=['nhood','count'],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
    )
)
m2.add_child(NIL)
m2.keep_in_front(NIL)


folium.LayerControl(collapsed=False).add_to(m2)
m2.save('SanFran1.html')

