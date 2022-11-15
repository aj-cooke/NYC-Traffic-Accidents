import pandas as pd


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


if __name__ == "__main__":
    ...
