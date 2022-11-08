# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 18:31:53 2022

@author: Andy
"""

import numpy as np 
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import datetime


class NYCCrashMatch:
    def __init__(self, master, m_points: list = ['botleft_long', 'botleft_lat',
                         'topleft_long', 'topleft_lat',
                         'topright_long', 'topright_lat',
                         'botright_long', 'botright_lat']):
    
        master['geometry'] = list(zip(zip(master[m_points[0]], master[m_points[1]]),
                             zip(master[m_points[2]], master[m_points[3]]),
                             zip(master[m_points[4]], master[m_points[5]]),
                             zip(master[m_points[6]], master[m_points[7]])))
        master['geometry'] = master['geometry'].apply(Polygon)
        master = gpd.GeoDataFrame(master, geometry='geometry')
        
        self.master = master
        self.m_points = m_points
    
    def ll_match(self, new, new_long: str, new_lat: str):
        """
        Matches to master street segments. m_points is list in form:
        [bottom left long, bottom left lat, top left long, top left lat, top right long,
        top right lat, bottom right long, bottom right lat]
        may need to handle duplicate matches
        returns new df with segmentID matched
        """
        new = new.dropna(subset = [new_long, new_lat])
        new['coords'] = list(zip(new[new_long],new[new_lat]))
        new['coords'] = new['coords'].apply(Point)

        new = gpd.GeoDataFrame(new, geometry='coords')
        
        print('Starting join: ', datetime.datetime.now())
        matches = gpd.tools.sjoin(new, self.master, predicate="within", how='left')
        print('Finished join: ', datetime.datetime.now())
        return matches
    
    def geom_match(self, new, new_geom: str, dim = 'point'):
        """
        Matches point to master areas if new is already an shp file
        """
        return gpd.tools.sjoin(new, self.master, predicate="within", how='left') \
            if dim == 'point' else gpd.tools.sjoin(new, self.master, how='left')
    
if __name__ == "__main__":
    m = pd.read_csv('ll_master.tsv', sep = "\t")
    m = NYCCrashMatch(m)
    collisions = pd.read_csv('Motor_Vehicle_Collisions_Crashes.csv')
    collisions_matched = m.ll_match(collisions, 'LONGITUDE', 'LATITUDE')
    collisions_matched.to_csv('collisions_matched.tsv', sep = "\t", index = False)
    
    speed_bumps = gpd.GeoDataFrame.from_file('geo_export_fa9d6a08-ceec-4cad-8539-7daacde49a0f.shp')
    speed_bumps['geometry'] = speed_bumps['geometry'].boundary
    speed_bumps_matched = m.geom_match(speed_bumps, 'geometry', dim = 'line')
    speed_bumps_matched.to_csv('speed_bumps_matched.csv', index = False)
    
    bike_lanes = gpd.GeoDataFrame.from_file('geo_export_d20fdaf8-b759-4bf8-9d53-7ec065a05922.shp')
    bike_lanes['geometry'] = bike_lanes['geometry'].boundary
    bike_lanes_matched = m.geom_match(bike_lanes, 'geometry', dim = 'line')
    bike_lanes_matched.to_csv('bike_lanes_matched.csv', index = False)
    
    speed_limits = gpd.GeoDataFrame.from_file('geo_export_3cf3daf0-3915-4815-99d6-3097f0d3e8f8.shp')
    speed_limits['geometry'] = speed_limits['geometry'].boundary
    speed_limits_matched = m.geom_match(speed_limits, 'geometry', dim = 'line')
    speed_limits_matched.to_csv('speed_limits_matched.csv', index = False)
    
    traffic = pd.read_csv('Traffic_Volume_Counts.csv')
    traffic_matched = pd.merge(traffic, m.master, left_on = ['Roadway Name', 'From', 'To'],
                               right_on = ['Roadway.Name', 'From', 'To'], how = 'left')
    traffic_matched.to_csv('traffic_matched.csv', index = False)
