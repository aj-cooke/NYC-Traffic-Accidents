# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 11:27:01 2022

@author: Andy
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep

segments = pd.read_csv('Documents/segments.csv')

def get_zips(df, street, c1, c2):
    df['int1'] = df[street] + "+%26+" + df[c1]
    df['int2'] = df[street] + "+%26+" + df[c2]
    df['int1'] = df['int1'].replace(' ', '+', regex = True)
    df['int2'] = df['int2'].replace(' ', '+', regex = True)
    df['zip1'] = 'X'
    df['zip2'] = 'X'
    
    for i in df.index:
        url = 'https://www.google.com/maps/place/' + df['int1'][i] + '+NY'
        req = requests.get(url)
        soup = str(BeautifulSoup(req.text, "html.parser"))
        if 'Our systems have detected unusual traffic' in soup:
            return df
        z = soup.find(", NY")
        df['zip1'][i] = soup[z + 5: z + 10]
        sleep(1.1)
        
        url = 'https://www.google.com/maps/place/' + df['int2'][i] + '+NY'
        req = requests.get(url)
        soup = str(BeautifulSoup(req.text, "html.parser"))
        if 'Our systems have detected unusual traffic' in soup:
            return df
        z = soup.find(", NY")
        df['zip2'][i] = soup[z + 5: z + 10]
        sleep(1.1)
        
        print(df['id'][i], df[street][i])
        
    return df

zips2 = get_zips(segments[segments['id'] >= 2390], 'Roadway.Name', 'From', 'To')
zips2 = zips2[zips2['id'] < 2390]
zips = pd.concat([zips, zips2], axis = 0)

# can also join lat and long
# draw lat long line on map, heat map to show traffic volume
