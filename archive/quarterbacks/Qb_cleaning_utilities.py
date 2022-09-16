import pandas as pd
import nfl_data_py as nfl
import datetime
from dateutil import relativedelta

# This class is built to produce a clean dataset for building a
# predictive model for quarterbacks.
class QB_Cleaning:
    # Constructor
    # Takes in a list of years as an input
    def __init__(self, years: list):
        self.id_data = self.__get_id_data()
        self.years = years
        self.qb_data_list = [self.__get_year_qb_data(year) for year in years]
        self.__clean_and_combine_data()
    # End of __init__()

    # Private method to set self.id_data
    def __get_id_data(self):
        ids = nfl.import_ids()
        cols = ['name', 
                'position', 
                'birthdate', 
                'height', 
                'weight', 
                'espn_id', 
                'gsis_id', 
                'draft_pick']
        return ids[cols]
    # End of __get_id_data()

    # Gets the qb data for the given year
    def __get_year_qb_data(self, year):
        qbr = self.__get_qbr_data(year)
        data = qbr.merge(self.id_data, left_on='player_id', right_on='espn_id', how='left', suffixes=('_qbr', '_id'))
        qb_basic = self.__get_qb_data(year)
        data = data.merge(qb_basic, left_on='gsis_id', right_on='player_id', how='left', suffixes=('_2', '_1'))
        data = data[data.position == 'QB'].copy()
        reindex_cols = ['espn_id', 
                        'season_1', 
                        'birthdate', 
                        'height', 
                        'weight', 
                        'draft_pick', 
                        'fantasy_points', 
                        'games', 
                        'ppr_sh', 
                        'completions',
                        'attempts', 
                        'passing_yards', 
                        'passing_tds', 
                        'interceptions', 
                        'rank', 
                        'qbr_total', 
                        'pts_added', 
                        'qb_plays', 
                        'epa_total', 
                        'pass', 
                        'run', 
                        'qbr_raw', 
                        'qualified',
                        'passing_air_yards', 
                        'passing_yards_after_catch', 
                        'passing_first_downs', 
                        'passing_epa', 
                        'passing_2pt_conversions', 
                        'dakota',
                        'carries', 
                        'rushing_yards', 
                        'rushing_tds', 
                        'rushing_fumbles', 
                        'rushing_fumbles_lost', 
                        'rushing_first_downs', 
                        'rushing_epa', 
                        'rushing_2pt_conversions', 
                        'sacks', 
                        'sack_yards', 
                        'sack_fumbles', 
                        'sack_fumbles_lost']
        data = data.reindex(columns=reindex_cols)
        data['season_1'] = pd.to_numeric(data['season_1'], downcast='integer')
        data.rename(columns={'season_1': 'season'}, inplace=True)
        fixed_date = datetime.datetime.strptime(f"{year}-12-31", '%Y-%m-%d').date()
        ages = []
        for row in data.itertuples():
            try:
                ages.append(relativedelta.relativedelta(fixed_date, datetime.datetime.strptime(str(row[3]), '%Y-%m-%d').date()).years)
            except:
                ages.append(None)



        data['birthdate'] = ages
        data.rename(columns={'birthdate': 'age'}, inplace=True)

        cols = ['fantasy_points', 
                'completions', 
                'attempts',
                'passing_yards', 
                'passing_tds', 
                'interceptions', 
                'passing_epa', 
                'carries', 
                'rushing_yards', 
                'rushing_tds', 
                'rushing_fumbles',
                'rushing_fumbles_lost', 
                'sack_fumbles',     
                'sack_fumbles_lost']
        for col in cols:
            data[col + "_per_game"] = data[col] / data['games']

        return data
    # End of __get_year_qb_data

    # Private method to get basic qb statistics
    # Input a year (e.x. 2019)
    def __get_qb_data(self, year):
        data = nfl.import_seasonal_data([year])
        keep = ['player_id', 
                'season', 
                'season_type', 
                'completions', 
                'attempts', 
                'passing_yards', 
                'passing_tds', 
                'interceptions', 
                'sacks', 
                'sack_yards',
                'sack_fumbles', 
                'sack_fumbles_lost', 
                'passing_air_yards', 
                'passing_yards_after_catch', 
                'passing_first_downs', 
                'passing_epa',
                'passing_2pt_conversions', 
                'dakota', 
                'carries', 
                'rushing_yards',
                'rushing_tds', 
                'rushing_fumbles', 
                'rushing_fumbles_lost', 
                'rushing_first_downs', 
                'rushing_epa', 
                'rushing_2pt_conversions',
                'fantasy_points', 
                'games', 
                'ppr_sh']
        return data[keep]
    # End of __get_qb_data

    # Private method to return qbr statistics
    # Input a year (e.x. 2019)
    def __get_qbr_data(self, year):
        qbr_data = nfl.import_qbr([year])
        qbr_data = qbr_data[qbr_data.season_type == 'Regular']
        qbr_data = qbr_data.drop(labels=['season_type', 'game_week', 'team_abb', 'name_short', 'name_first', 'name_last', 'exp_sack', 'sack', 'penalty'], axis=1)
        return qbr_data
    # End of __get_qbr_data()

    # Returns the list of data
    def get_data(self):
        return self.qb_data
    # End of get_data()

    # Merges Data
    def __clean_and_combine_data(self):
        data = self.qb_data_list
        drop_cols = ['age',
                     'season', 
                     'height',
                     'weight',
                     'draft_pick']
        for i in range(len(data) - 1, 1, -1):
            data[i] = data[i].merge(data[i - 1].drop(labels=drop_cols, axis=1), 
                                    on='espn_id', how='left', suffixes=['', '_n-1'])
            data[i] = data[i].merge(data[i - 2].drop(labels=drop_cols, axis=1),
                                    on='espn_id', how='left', suffixes=['', '_n-2'])
        for i in range(len(data) - 1):
            next_year = data[i + 1][['espn_id', 'fantasy_points', 'fantasy_points_per_game']]
            data[i] = data[i].merge(next_year, on='espn_id', how='left', suffixes=['', '_next_year'])
        combined = pd.DataFrame()
        for df in data:
            combined = pd.concat([combined, df])
        self.qb_data = combined
    # End of __clean_and_combine_data()

    # Returns id data
    def get_player_info(self):
        return self.id_data