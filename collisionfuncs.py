import pandas as pd
import geoplot as gplt
import geopandas as gpd
import geofuncs


def rate(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    This function calculates injury rate or fatality rate in each streetID among all the collisions.

    Args:
        data (pd.DataFrame): collisions data
        column (str): the name of the column to be used to calculate injury rate or fatality rate

    Returns: pd.DataFrame that contains 'CRASH DATE', 'CRASH TIME', 'BOROUGH', 'streetID', 'lat1', 'long1', and column.
    """
    data = data.loc[:, ['CRASH DATE', 'CRASH TIME',
                        'BOROUGH', 'streetID', 'lat1', 'long1', column]]
    data = data.dropna(how='any')
    rate = data.groupby(by=['streetID'], as_index=False).agg(
        {'CRASH DATE': 'first',
         'CRASH TIME': 'first',
         'BOROUGH': 'first',
         'streetID': 'first',
         'lat1': 'first',
         'long1': 'first',
         column: 'mean'})
    return rate


def pointplot(data: pd.DataFrame, colname: str, title: str=None):
    """
    This function plots injury rate or fatality rate on a NYC map.

    Args:
        data (pd.DataFrame): collisions data
        column (str): the name of the column to be used to calculate injury rate or fatality rate
        title (str): the title of the plot

    Returns: the plot axes
    """
    boroughs = gpd.read_file(gplt.datasets.get_path('nyc_boroughs'))
    injury_rate = rate(data, colname)
    rate_geo = geofuncs.to_geojson(injury_rate, 'lat1', 'long1', [
        colname])

    proj = gplt.crs.AlbersEqualArea(
        central_latitude=40.7128, central_longitude=-74.0059)
    ax = gplt.polyplot(
        boroughs,
        projection=proj,
        figsize=(10, 10))
    gplt.pointplot(
        rate_geo,
        projection=proj,
        ax=ax,
        hue=colname,
        cmap='Purples',
        scheme='quantiles',
        scale=colname,
        legend=True,
        legend_var='hue',)
    if not title:
        title = colname + ' in Crashes in New York City'
    ax.set_title(title)

    return ax


if __name__ == "__main__":
    ...
