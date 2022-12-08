import pandas as pd
import geopandas as gpd
from shapely import wkt


class CollisionFeature:
    def __init__(self, collisions: pd.DataFrame, speed_bumps_matched: pd.DataFrame, speed_limits_matched: pd.DataFrame, bike_lanes_matched: pd.DataFrame):
        """
        Create freatures that will be used in building collision models

        Parameter
        -----------
        collisions: pd.DataFrame
        speed_bumps_matched: pd.DataFrame
        speed_limits_matched: pd.DataFrame
        bike_lanes_matched: pd.DataFrame
        """
        self.collisions = collisions
        self.speed_bump = speed_bumps_matched.loc[:, ['streetID', 'new_humps']]
        self.speed_limits = speed_limits_matched.loc[:, [
            'streetID', 'postvz_sl']]
        self.bike_lane = bike_lanes_matched.loc[:, ['streetID', 'lanecount']]

        # below is to clean collisions table
        # filter out false LATITUDE and LONGITUDE
        criterion1 = (self.collisions['LATITUDE'] > 38) & (self.collisions['LATITUDE'] < 42) & (
            self.collisions['LONGITUDE'] < -72) & (self.collisions['LONGITUDE'] > -76)
        # filter entries with matched streetID
        criterion2 = self.collisions['streetID'].notnull()
        self.collisions = self.collisions[criterion1 & criterion2]
        # add two columns: days of week and hour
        self.collisions.loc[:, ['CRASH DATE']] = pd.to_datetime(
            self.collisions['CRASH DATE'])
        # Monday=0, Sunday=6.
        self.collisions.loc[:, ['dayofweek']
                            ] = self.collisions['CRASH DATE'].dt.dayofweek
        self.collisions.loc[:, ['time']] = pd.to_datetime(
            self.collisions['CRASH TIME']).dt.hour  # int64

    def speed_bumps(self) -> pd.DataFrame:
        """
        Add an indicator variable for whether the street has a speed bump on the collisions table. Inplace replace. The column name is speed_bumps.

        Parameter
        -----------
        None

        Returns
        -----------
        collisions added one ore column indicate if the stree has a speed bump. 
        """
        # merge speedbump with traffic and collision
        self.collisions = pd.merge(
            self.collisions, self.speed_bump, how='left', on='streetID')

        # 1 if present and 0 if not present
        self.collisions['new_humps'].loc[~self.collisions['new_humps'].isnull()] = 1
        self.collisions['new_humps'].loc[self.collisions['new_humps'].isnull()] = 0
        self.collisions.rename(
            columns={'new_humps': 'speed_bumps'}, inplace=True)

        return self.collisions

    def speed_limit(self) -> pd.DataFrame:
        """
        Add an indicator variable for whether the street has a speed limit on the collisions table. Inplace replace. The column name is speed_limits.

        Parameter
        -----------
        None

        Returns
        -----------
        collisions added one ore column indicate if the stree has a speed limit.

        """
        self.collisions = pd.merge(
            self.collisions, self.speed_limits, how='left', on='streetID')
        self.collisions['postvz_sl'].mask(
            self.collisions['postvz_sl'] > 1, 1, inplace=True)
        self.collisions.rename(
            columns={'postvz_sl': 'speed_limits'}, inplace=True)

        return self.collisions

    def bike_lanes(self) -> pd.DataFrame:
        """
        Add an indicator variable for whether the street has a speed limit on the collisions table. Inplace replace. The column name is bike_lanes.

        Parameter
        -----------
        None

        Returns
        -----------
        collisions added one ore column indicate if the stree has bike lanes.

        """
        self.collisions = pd.merge(
            self.collisions, self.bike_lane, how='left', on='streetID')
        self.collisions['lanecount'].loc[~self.collisions['lanecount'].isnull()] = 1
        self.collisions['lanecount'].loc[self.collisions['lanecount'].isnull()] = 0
        self.collisions.rename(
            columns={'lanecount': 'bike_lanes'}, inplace=True)

        return self.collisions


class TrafficFeature:
    def __init__(self, traffic_matched: pd.DataFrame):
        """
        Create freatures that will be used in building collision models from the traffic table

        Parameter
        -----------
        traffic_matched: pd.DataFrame
        """
        # below is to clean traffic table
        self.traffic = traffic_matched
        self.traffic.rename(columns={'12:00-1:00 AM': '0', '1:00-2:00AM': '1', '2:00-3:00AM': '2', '3:00-4:00AM': '3',
                                     '4:00-5:00AM': '4', '5:00-6:00AM': '5', '6:00-7:00AM': '6', '7:00-8:00AM': '7',
                                                    '8:00-9:00AM': '8', '9:00-10:00AM': '9', '10:00-11:00AM': '10', '11:00-12:00PM': '11',
                                                    '12:00-1:00PM': '12', '1:00-2:00PM': '13', '2:00-3:00PM': '14', '3:00-4:00PM': '15',
                                                    '4:00-5:00PM': '16', '5:00-6:00PM': '17', '6:00-7:00PM': '18', '7:00-8:00PM': '19',
                                                    '8:00-9:00PM': '20', '9:00-10:00PM': '21', '10:00-11:00PM': '22', '11:00-12:00AM': '23'}, inplace=True)
        self.traffic.dropna(subset=['geometry'], inplace=True)
        self.traffic['geometry'] = self.traffic['geometry'].astype(
            str).apply(wkt.loads)
        self.traffic = gpd.GeoDataFrame(self.traffic, geometry='geometry')
        self.traffic = pd.melt(self.traffic, id_vars=['Date', 'geometry', 'streetID'],
                               value_vars=list(self.traffic.columns[7:31]),
                               var_name='time', value_name='traffic')
        self.traffic['area'] = self.traffic['geometry'].area
        self.traffic = self.traffic[self.traffic['area'] < 2e-5]
        self.traffic['time'] = self.traffic['time'].apply(lambda x: int(x))
        self.traffic = self.traffic.drop(['geometry', 'area'], axis=1)
        self.traffic['Date'] = pd.to_datetime(self.traffic['Date'])
        self.traffic['dayofweek'] = self.traffic['Date'].dt.dayofweek
        self.traffic['month'] = self.traffic['Date'].dt.month
        self.traffic['streetID'] = self.traffic['streetID'].apply(
            lambda x: int(x))

    def traffic_byhour(self) -> pd.DataFrame:
        """
        This function takes self.traffic and aggregates it by streetID and hour.

        Parameter
        -----------
        self.traffic_matched: pd.DataFrame

        Returns
        -----------
        self.traffic_byhour: pd.DataFrame. Columns are streetID, time, meanHour, stdHour, medianHour, minHour, maxHour, rangeHour.
        time is from 0 to 23. 0 denotes 0:00 to 0:59, and 23 denotes 23:00 to 23:59.
        """
        traffic_byhour = self.traffic.groupby(by=['streetID', 'time']).agg(
            {'traffic': ['mean', 'std', 'median', 'min', 'max']})
        traffic_byhour.columns = traffic_byhour.columns.droplevel(0)
        traffic_byhour = traffic_byhour.reset_index()
        traffic_byhour['rangeHour'] = traffic_byhour.apply(
            lambda row: row['max'] - row['min'], axis=1)
        traffic_byhour = traffic_byhour.rename(
            columns={'mean': 'meanHour', 'std': 'stdHour', 'median': 'medianHour', 'min': 'minHour', 'max': 'maxHour'})
        return traffic_byhour

    def traffic_bydayofweek(self) -> pd.DataFrame:
        """
        This function takes self.traffic and aggregates it by streetID and hour.

        Parameter
        -----------
        self.traffic_matched: pd.DataFrame

        Returns
        -----------
        self.traffic_byhour: pd.DataFrame. Columns are streetID, dayofweek, meanWeek, stdWeek, medianWeek, minWeek, maxWeek, rangeWeek.
        dayofweek means which day of the week. 0 is Monday, and 7 is Sunday.
        """
        traffic_bydayofweek = self.traffic.groupby(by=['streetID', 'dayofweek']).agg(
            {'traffic': ['mean', 'std', 'median', 'min', 'max']})
        traffic_bydayofweek.columns = traffic_bydayofweek.columns.droplevel(0)
        traffic_bydayofweek = traffic_bydayofweek.reset_index()
        traffic_bydayofweek['rangeWeek'] = traffic_bydayofweek.apply(
            lambda row: row['max'] - row['min'], axis=1)
        traffic_bydayofweek = traffic_bydayofweek.rename(
            columns={'mean': 'meanWeek', 'std': 'stdWeek', 'median': 'medianWeek', 'min': 'minWeek', 'max': 'maxWeek'})
        return traffic_bydayofweek


if __name__ == "__main__":
    path = '/Users/daixinming/Documents/Graduate_School/2022_Fall/Seminar/stat_project/matched_data/crash_matched_data'

    collisions = pd.read_csv(
        path + '/collisions_matched.tsv', sep='\t', nrows=200)
    traffic_matched = pd.read_csv(
        path + '/traffic_matched.csv')
    speed_limits_matched = pd.read_csv(
        path + '/speed_limits_matched.csv')
    speed_bumps_matched = pd.read_csv(
        path + '/speed_bumps_matched.csv')
    bike_lanes_matched = pd.read_csv(
        path + '/bike_lanes_matched.csv')

    # Create features
    # Use the CollisionFreature class from collision_model_features.py to add 3 indicator variables for speed bumps, speed limits, and bike lanes to the collisions table
    feature = CollisionFeature(
        collisions, speed_bumps_matched, speed_limits_matched, bike_lanes_matched)
    feature.speed_bumps()
    feature.speed_limit()
    feature.bike_lanes()
    # Use the TrafficFeature class to get the traffic volumes
    traffic_feature = TrafficFeature(traffic_matched)
    traffic_byhour = traffic_feature.traffic_byhour()
    traffic_bydayofweek = traffic_feature.traffic_bydayofweek()

    feature.collisions.to_csv(path + "/new_collisions.csv")
    traffic_byhour.to_csv(path + "/traffic_byhour.csv")
    traffic_bydayofweek.to_csv(path + "/traffic_bydayofweek.csv")
