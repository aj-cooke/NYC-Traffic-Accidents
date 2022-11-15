import pandas as pd
import geojson


def to_geojson(data: pd.DataFrame, properties: str) -> geojson.GeoJSON:
    """
    This function covert data from pd.DataFrame to geojson data structure. Rows with NAs will be neglected in the geojson.

    Args:
        data (pd.DataFrame): the data frame that includes ['LATITUDE', 'LONGITUDE'] and properties columns
        properties (str): the column name to be contained in the geojson data structure

    Returns: geojson.GeoJSON
    """
    data = data.loc[:, ['LATITUDE', 'LONGITUDE', properties]]
    data = data.dropna(how='any')
    lat_long = data.apply(lambda row: geojson.Feature(geometry=geojson.Point((float(row['LATITUDE']), float(row['LONGITUDE']))),
                                                      properties={properties: row[properties]}),
                          axis=1)
    data_geo = geojson.FeatureCollection(
        features=lat_long)
    return data_geo


if __name__ == "__main__":
    ...
