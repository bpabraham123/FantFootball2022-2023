import pandas as pd
import nfl_data_py as nfl
import datetime
from dateutil import relativedelta



class FlexCleaningUtilities:
    def __init__(self, positions: list=['RB', 'WR', 'TE'], years: list=range(2013, 2022)):
        for item in positions:
            if item not in ['RB', 'WR', 'TE']:
                raise ValueError('Invalid position')
        if len(positions) > 3:
            raise ValueError('Too many positions')
        if len(positions) == 0:
            raise ValueError('No positions')
        
        for year in years:
            if year not in range(2013, 2022):
                raise ValueError('Invalid year')
        if len(years) == 0:
            raise ValueError('No years')
        
        self.positions = positions
        self.years = years
        self.yearly_data = {year: pd.DataFrame() for year in years}

    def __get_seasonal_data(self, year):
        return nfl.import_seasonal_data([year])

    def __get_id_data(self):
        ids = nfl.import_ids()
        if len(self.positions) == 1:
            return ids[ids.position == self.positions[0]]
        elif len(self.positions) == 2:
            return ids[(ids.position == self.positions[0]) | 
                       (ids.position == self.positions[1])]
        elif len(self.positions) == 3:
            return ids[(ids.position == self.positions[0]) | 
                       (ids.position == self.positions[1]) | 
                       (ids.position == self.positions[2])]

    def __get_snap_count_data(self, year):
        snaps = nfl.import_snap_counts([year])
        grouped_df = snaps[snaps.position == 'RB'].groupby(['pfr_player_id', 'player', 'season']).median()
        return grouped_df[['offense_snaps', 'offense_pct']]

    def __get_complete_season_data(self, year):
        season_data = self.__get_seasonal_data(year)
        id_data = self.__get_id_data()
        snap_count_data = self.__get_snap_count_data(year)

        data = id_data.merge(season_data, left_on='gsis_id', right_on='player_id', how='inner')
        data = data.merge(snap_count_data, left_on='pfr_id', right_on='pfr_player_id', how='left')
        data = data[data.season_type == 'REG'].copy()

        data = data.reindex(columns=['name', 'position', 'team', 'birthdate', 'draft_pick', 
                                     'height', 'weight', 'draft_year', 'season',
                                     'player_id', 'carries', 'rushing_yards', 'rushing_tds', 
                                     'rushing_fumbles', 'rushing_fumbles_lost',
                                     'rushing_first_downs', 'rushing_epa', 'rushing_2pt_conversions', 
                                     'receptions', 'targets', 'receiving_yards', 'receiving_tds', 
                                     'receiving_air_yards', 'receiving_yards_after_catch', 
                                     'receiving_first_downs', 'receiving_epa', 'fantasy_points_ppr', 
                                     'games', 'tgt_sh', 'ay_sh', 'yac_sh', 'wopr', 'ry_sh', 'rtd_sh', 
                                     'rfd_sh', 'rtdfd_sh', 'dom', 'w8dom', 'yptmpa',
                                     'ppr_sh', 'offense_snaps', 'offense_pct'])

        data['draft_year'] = data['season'] - data['draft_year']
        data.rename(columns={'draft_year': 'experience'}, inplace=True)

        ages = []
        fixed_date = datetime.datetime.strptime(f"{year}-12-31", '%Y-%m-%d').date()
        ages = []
        for row in data.itertuples():
            try:
                val = relativedelta.relativedelta(fixed_date, datetime.datetime.strptime(str(row[4]), '%Y-%m-%d').date()).years
                ages.append(val)
            except:
                ages.append(None)


        data['birthdate'] = ages
        data.rename(columns={'birthdate': 'age'}, inplace=True)

        data = data.reindex(columns=['player_id', 'season', 'age', 'height', 'weight', 'experience', 'draft_pick', 'games',
                                     'carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles',
                                     'rushing_fumbles_lost', 'rushing_first_downs', 'rushing_epa',
                                     'rushing_2pt_conversions', 'receptions', 'targets', 'receiving_yards',
                                     'receiving_tds', 'receiving_air_yards', 'receiving_yards_after_catch',
                                     'receiving_first_downs', 'receiving_epa', 'fantasy_points_ppr', 'tgt_sh',
                                     'ay_sh', 'yac_sh', 'wopr', 'ry_sh', 'rtd_sh', 'rfd_sh', 'rtdfd_sh', 'dom',
                                     'w8dom', 'yptmpa', 'ppr_sh', 'offense_snaps', 'offense_pct'])
        
        per_game = ['carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles',
                    'rushing_fumbles_lost', 'rushing_first_downs', 'rushing_epa',
                    'rushing_2pt_conversions', 'receptions', 'targets', 'receiving_yards',
                    'receiving_tds', 'receiving_air_yards', 'receiving_yards_after_catch',
                    'receiving_first_downs', 'receiving_epa', 'fantasy_points_ppr']

        for col_name in per_game:
            data[col_name + "_per_game"] = data[col_name] / data['games']
        
        data = data.sort_values(by='fantasy_points_ppr', ascending=False)
        data = data.reset_index(drop=True)
        data['fantasy_rank'] = data.index + 1

        data = data.sort_values(by='fantasy_points_ppr_per_game', ascending=False)
        data = data.reset_index(drop=True)
        data['per_game_fantasy_rank'] = data.index + 1
        
        return data

    def compile_data(self):
        for year in self.years:
            self.yearly_data[year] = self.__get_complete_season_data(year)
    
    def get_data(self, year=None):
        if year is None:
            return self.yearly_data
        return self.yearly_data[year]
    

def getFlexPositionData(position):
    if position != 'RB' and position != 'WR' and position != 'TE':
        raise ValueError('Position must be RB, WR, or TE')
    
    flex_cleaning_obj = FlexCleaningUtilities([position])
    flex_cleaning_obj.compile_data()
    yearly_data = flex_cleaning_obj.get_data()
    drop_cols = ['age', 'height', 'weight', 'experience', 'draft_pick', 'season']
    for year in range(2021, 2014, -1):
        yearly_data[year] = yearly_data[year].merge(yearly_data[year - 1].drop(drop_cols, axis=1), 
                                                left_on='player_id', 
                                                right_on='player_id', 
                                                how='left',
                                                suffixes=['', '_n-1'])
        yearly_data[year] = yearly_data[year].merge(yearly_data[year - 2].drop(drop_cols, axis=1), 
                                                left_on='player_id', 
                                                right_on='player_id', 
                                                how='left',
                                                suffixes=['', '_n-2'])
    
    for year in range(2013, 2021):
        yearly_data[year] = yearly_data[year].merge(yearly_data[year + 1][['player_id', 'fantasy_points_ppr', 'fantasy_points_ppr_per_game', 'fantasy_rank', 'per_game_fantasy_rank']], 
                                                left_on='player_id', 
                                                right_on='player_id', 
                                                how='left',
                                                suffixes=['', '_future'])
    
    combined_data = pd.DataFrame()
    for year in range(2013, 2022):
        combined_data = pd.concat([combined_data, yearly_data[year]], axis=0)
    
    return combined_data

def getCurrentData(position):
    if position != 'RB' and position != 'WR' and position != 'TE':
        raise ValueError('Position must be RB, WR, or TE')
    currentYear = datetime.datetime.today().year
    flex_cleaning_obj = FlexCleaningUtilities(positions=[position], years=range(currentYear - 2, currentYear + 1))
    flex_cleaning_obj.compile_data()
    yearly_data = flex_cleaning_obj.get_data()
    drop_cols = ['age', 'height', 'weight', 'experience', 'draft_pick']
    yearly_data[currentYear] = yearly_data[currentYear].merge(yearly_data[currentYear - 1].drop(drop_cols, axis=1), 
                                                left_on='player_id', 
                                                right_on='player_id', 
                                                how='left',
                                                suffixes=['', '_n-1'])
    yearly_data[currentYear] = yearly_data[currentYear].merge(yearly_data[currentYear - 2].drop(drop_cols, axis=1), 
                                                left_on='player_id', 
                                                right_on='player_id', 
                                                how='left',
                                                suffixes=['', '_n-2'])
    return yearly_data[currentYear]