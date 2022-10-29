from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep

segments = pd.read_csv('Documents/segments.csv')

def get_zip_lat_long(df, street, c1, c2):
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
        
    # make the actual lat and long columns
    df[['lat1', 'long1']] = df['ll1'].str.split(',', expand=True)
    df[['lat2', 'long2']] = df['ll1'].str.split(',', expand=True)
    
    return df

zips2 = get_zip_lat_long(segments[segments['id'] < 2], 'Roadway.Name', 'From', 'To')
#zips2 = zips2[zips2['id'] < 2390]
#zips = pd.concat([zips, zips2], axis = 0)
