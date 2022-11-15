import pandas as pd
import geopandas as gpd
import geojson
from typing import List


def to_geojson(data: pd.DataFrame, latitude: str, longitude: str, properties: List[str]) -> gpd.GeoDataFrame:
    """
    This function coverts data from pd.DataFrame to gpd.GeoDataFrame. Rows with NAs will be neglected in the gpd.GeoDataFrame.

    Args:
        data (pd.DataFrame): the data frame that includes ['LATITUDE', 'LONGITUDE'] and properties columns
        properties (List[str]): column names to be contained in the geojson data structure

    Returns: gpd.GeoDataFrame
    """
    colnames = [latitude, longitude]
    colnames.extend(properties)
    data = data.loc[:, colnames]
    data = data.dropna(how='any')
    lat_long = data.apply(lambda row: geojson.Feature(geometry=geojson.Point((float(row[longitude]), float(row[latitude]))),
                                                      properties={pro: row[pro] for pro in properties}),
                          axis=1)
    feature_coll = geojson.FeatureCollection(
        features=lat_long)
    data_geo = gpd.GeoDataFrame.from_features(feature_coll['features'])
    return data_geo


if __name__ == "__main__":
    data = pd.read_csv(
        "/Users/daixinming/Documents/Graduate_School/2022_Fall/Seminar/stat_project/matched_data/crash_matched_data/collisions_matched.tsv", sep='\t', nrows=200)
    print(to_geojson(data, 'lat1', 'long1', [
          'NUMBER OF PERSONS INJURED', 'streetID']))
