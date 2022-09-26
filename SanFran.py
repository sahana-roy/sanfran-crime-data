#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 09:22:00 2022

@author: sahanaroy
"""

import pandas as pd
df = pd.read_csv("train.csv")
df.head(5)
list(df.columns)

df1 = df.head(500)

import folium

#map1 = folium.Map(
#    location=[-122.39958770418998, 37.7350510103906],
#    tiles='cartodbpositron',
#    zoom_start=12,
#)

# San Francisco latitude and longitude values
latitude = 37.77
longitude = -122.42
sf_neighborhood_geo = 'Current Police Districts.geojson'

# Create map
map1 = folium.Map(
       location=[latitude,longitude],
       zoom_start=12)

df1.apply(lambda row:folium.CircleMarker(location=[row["Y"], row["X"]]).add_to(map1), axis=1)
map1.save("SanFran1.html")

map2 = folium.Map(
       location=[latitude,longitude],
       zoom_start=12)
for index, row in df1.iterrows():
    folium.CircleMarker([row['Y'], row['X']],
                        radius=3,
                        popup=row['Category'],
                        fill_color="#3db7e4", # divvy color
                       ).add_to(map2)
map2.save("SanFran2.html")

from folium import plugins
from folium.plugins import MarkerCluster
# convert to (n, 2) nd-array format for heatmap
dfmatrix = df1[['Y', 'X']].values
# plot heatmap
map2.add_child(plugins.HeatMap(dfmatrix, radius=15))
map2.save("SanFran3.html")

#Chloropeth

# group by neighborhood
import geopandas as gpd

districts_full = gpd.read_file('Current Police Districts.geojson')
#districts = districts_full[["district", "geometry"]].set_index("district")
districts = districts.sort_values('district')
districts.head()

# Number of crimes in each police district
df2 = df1.groupby('PdDistrict').count()
df2 = pd.DataFrame(df2,columns=['Category'])  # remove unneeded columns
df2.reset_index(inplace=True)   # default index, otherwise groupby column becomes index
df2.rename(columns={'PdDistrict':'district','Category':'count'}, inplace=True)
df2.sort_values(by='district', inplace=True, ascending=True)

#Check
print('Length of dataframe: ',len(df2),'Length of district list: ',len(districts))

# Add a choropleth map to the base map

#df2['Neighborhood'] = df2['Neighborhood'].astype('str')

# we rename the column from id to state in the geoJSON_df so we can merge the two data frames.
# Next we merge our sample data (df) and the geoJSON data frame on the key id.
final_df = districts.merge(df2, on = "district")
final_df.head()

#map3 = folium.Map(
#       location=[latitude,longitude],
#       zoom_start=12)

folium.Choropleth(
       geo_data=final_df,
       data=final_df,
       columns=['district','count'],
       key_on='feature.properties.district',
       fill_color='YlOrRd',
       fill_opacity='0.7',
       line_opacity='0.2',
       legend_name='Crime Rate in San Francisco, by Neighborhood').add_to(map2)
folium.LayerControl().add_to(map2)
map2.save("SanFran5.html")

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
        fields=['district','count'],
        aliases=['district','count'],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
    )
)
map2.add_child(NIL)
map2.keep_in_front(NIL)

map2.save("SanFran6.html")


