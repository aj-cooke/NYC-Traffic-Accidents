# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 18:31:53 2022

@author: Andy
"""

import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def in_polygon(point1, point2, lat1, long1, lat2, long2, lat3, long3, lat4, long4):
    return Polygon([(lat1, long1),(lat2, long2),(lat3, long3),(lat4, long4)]).contains(Point(point1, point2))
    
in_polygon = np.vectorize(in_polygon)

def get_index(lst, val):
    try:
        return lst.index(val)
    except:
        return -1

def poly_match(point1, point2, lat1, long1, lat2, long2, lat3, long3, lat4, long4):
    return get_index(list(in_polygon(point1, point2, lat1, long1, lat2, long2, lat3, long3, lat4, long4)), True)

def street_match(master, master_ll_cols: list, new, new_ll_cols: list):    
    new['streedID'] = new.apply(lambda x: poly_match(x[new_ll_cols[0]],x[new_ll_cols[1]],
                                                     np.array(master[master_ll_cols[0]]), np.array(master[master_ll_cols[1]]), 
                                                     np.array(master[master_ll_cols[2]]), np.array(master[master_ll_cols[3]]), 
                                                     np.array(master[master_ll_cols[4]]), np.array(master[master_ll_cols[5]]), 
                                                     np.array(master[master_ll_cols[6]]), np.array(master[master_ll_cols[7]])), 
                                axis = 1)
    return new


if __name__ == "__main__":
    mm = pd.DataFrame({'lat1': np.zeros(100),
                   'long1': np.zeros(100),
                   'lat2': np.zeros(100),
                   'long2': np.ones(100),
                   'lat3': np.ones(100),
                   'long3': np.ones(100),
                   'lat4': np.ones(100),
                   'long4': np.zeros(100)})

    df = pd.DataFrame({'lat': [0.5, 1], 'long':[0.5,1]})
    street_match(mm, ['lat1', 'long1', 'lat2', 'long2', 'lat3', 'long3', 'lat4', 'long4'], df, ['lat', 'long'])

