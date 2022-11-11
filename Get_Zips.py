# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 11:27:01 2022

@author: Andy
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from time import sleep


class NYCCollisions:    
    def zip_lat_long(self, segments, street, c1, c2):
        df = segments.copy()
        df['int1'] = df[street] + "+%26+" + df[c1]
        df['int2'] = df[street] + "+%26+" + df[c2]
        df['int1'] = df['int1'].replace(' ', '+', regex = True)
        df['int2'] = df['int2'].replace(' ', '+', regex = True)
        df['zip1'] = 'X'
        df['zip2'] = 'X'
        df['ll1'] = 'X'
        df['ll2'] = 'X'
        
        for i in df.index:
            url = 'https://www.google.com/maps/place/' + df['int1'][i] + '+NY'
            req = requests.get(url)
            soup = str(BeautifulSoup(req.text, "html.parser"))
            if 'Our systems have detected unusual traffic' in soup:
                return df
            z = soup.find(", NY")
            df['zip1'][i] = soup[z + 5: z + 10]
            ll = soup.find(";ll=")
            df['ll1'][i] = soup[ll + 4: ll + 24]
            sleep(1.1)
            
            url = 'https://www.google.com/maps/place/' + df['int2'][i] + '+NY'
            req = requests.get(url)
            soup = str(BeautifulSoup(req.text, "html.parser"))
            if 'Our systems have detected unusual traffic' in soup:
                return df
            z = soup.find(", NY")
            df['zip2'][i] = soup[z + 5: z + 10]
            ll = soup.find(";ll=")
            df['ll2'][i] = soup[ll + 4: ll + 24]
            sleep(1.1)
            print(df['id'][i], df[street][i])
        return df
    
    def boundaries_from_ll(self, zip_ll, alpha):
        df = zip_ll.copy()
        # make the actual lat and long columns
        df[['lat1', 'long1']] = df['ll1'].str.split(',', expand=True)
        df['lat1'] = pd.to_numeric(df['lat1'], errors = 'coerce')
        df['long1'] = pd.to_numeric(df['long1'], errors = 'coerce')
        df[['lat2', 'long2']] = df['ll2'].str.split(',', expand=True)
        df['lat2'] = pd.to_numeric(df['lat2'], errors = 'coerce')
        df['long2'] = pd.to_numeric(df['long2'], errors = 'coerce')
        
        df['top_lat'] = np.where(df['lat1'] > df['lat2'], df['lat1'], df['lat2'])
        df['right_long'] = np.where(df['long1'] > df['long2'], df['long1'], df['long2'])
        df['bot_lat'] = np.where(df['lat1'] < df['lat2'], df['lat1'], df['lat2'])
        df['left_long'] = np.where(df['long1'] < df['long2'], df['long1'], df['long2'])
        
        for ik, iv in {'bot':-1, 'top':1}.items():
            for xk, xv in {'right':1, 'left':-1}.items():
                df[f"{ik}{xk}_lat"] = df[f"{ik}_lat"] + alpha*(iv)
                df[f"{ik}{xk}_long"] = df[f"{xk}_long"] + alpha*(xv)
                
        return df


if __name__ == "__main__":
    segments = pd.read_csv('segments.csv')
    cons = NYCCollisions()
    zips = cons.zip_lat_long(segments, 'Roadway.Name', 'From', 'To') # need to repeat and concat, requests get denied
    zips = cons.boundaries_from_ll(zips, 0.00013)
    zips.to_csv('zip_ll_bound.tsv', sep = '\t', index = False)

