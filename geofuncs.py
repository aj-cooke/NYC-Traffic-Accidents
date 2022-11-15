import pandas as pd
import geopandas as gpd
import geojson


def to_geojson(data: pd.DataFrame, property: str) -> gpd.GeoDataFrame:
    """
    This function covert data from pd.DataFrame to gpd.GeoDataFrame. Rows with NAs will be neglected in the gpd.GeoDataFrame.

    Args:
        data (pd.DataFrame): the data frame that includes ['LATITUDE', 'LONGITUDE'] and properties columns
        properties (str): the column name to be contained in the geojson data structure

    Returns: gpd.GeoDataFrame
    """
    data = data.loc[:, ['LATITUDE', 'LONGITUDE', property]]
    data = data.dropna(how='any')
    lat_long = data.apply(lambda row: geojson.Feature(geometry=geojson.Point((float(row['LATITUDE']), float(row['LONGITUDE']))),
                                                      properties={property: row[property]}),
                          axis=1)
    feature_coll = geojson.FeatureCollection(
        features=lat_long)
    data_geo = gpd.GeoDataFrame.from_features(feature_coll['features'])
    return data_geo


if __name__ == "__main__":
    ...
