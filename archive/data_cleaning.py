
import pandas as pd
import nfl_data_py as nfl

class Data_Cleaning:
    def __init__(self, years: list):
        self.years = years
        self.data = nfl.import_seasonal_data(years)
        self.ids = nfl.import_ids()
        self.ids = self.ids[['espn_id', 'gsis_id', 'name', 'position',
                             'draft_round', 'draft_pick', 'height', 'weight']]
        #self.ids.set_index('pfr_index', inplace=True)
        #self.qb_data = pd.DataFrame
        #self.rb_data = pd.DataFrame
        #self.wr_data = pd.DataFrame
        #self.te_data = pd.DataFrame
        self.ids.head()

    # This function needs to access the qbr data and the seasonal data
    # and join them together.
    def clean_qb_data(self, year):
        qbr_data = nfl.import_qbr(years=[year])
        seasonal_data = self.data[(self.data)['season']==year]
        qbr_and_ids = qbr_data.merge(self.ids, left_on='player_id', right_on='espn_id', suffixes=('', '_r1'))

        #qbr_and_ids = qbr_data.join(self.ids, on='espn_id')
        #combined_df = qbr_and_ids.join(seasonal_data, on='gsis_id')
        combined_df = qbr_and_ids.merge(seasonal_data, left_on='gsis_id', right_on='player_id', suffixes=('', '_r2'))
        combined_df = combined_df[combined_df['position'] == 'QB']
        combined_df = combined_df[combined_df['season_type'] == 'Regular']
        combined_df = combined_df.drop(columns=['season_type', 'game_week', 'team_abb',
                                                'player_id', 'exp_sack', 'penalty',
                                                'sack', 'name_first', 'name_last',
                                                'name_display', 'player_id_r2',
                                                'season_r2', 'season_type_r2',
                                                'sacks', 'sack_yards', 'receptions', 'targets',
                                                'receiving_yards', 'receiving_tds', 'receiving_tds',
                                                'receiving_fumbles', 'receiving_fumbles_lost',
                                                'receiving_air_yards', 'receiving_yards_after_catch',
                                                'receiving_first_downs', 'receiving_epa', 'receiving_2pt_conversions',
                                                'special_teams_tds', 'tgt_sh', 'ay_sh', 'yac_sh',
                                                'ry_sh', 'rtd_sh', 'rfd_sh', 'rtdfd_sh',
                                                'dom', 'w8dom', 'yptmpa'])
        return combined_df

    # This function needs to iterate through the years in the dataframe and call
    # clean_qb_data on each year. Then it needs to combine the dataframes
    # together such that each row has data from the past three years,
    # and the next years ppg
    def join_qb_data(self):
        list_qb_data = []
        for year in self.years:
            list_qb_data.append(self.clean_qb_data(year))

        # gets past data
        for i in range(len(list_qb_data) - 2):
            list_qb_data[i + 1] = list_qb_data[i + 1].merge(list_qb_data[i],
                                                            left_on='espn_id',
                                                            right_on='espn_id',
                                                            suffixes=('', '_n-1'))
            list_qb_data[i + 2] = list_qb_data[i + 2].merge(list_qb_data[i],
                                                            left_on='espn_id',
                                                            right_on='espn_id',
                                                            suffixes=('', '_n-2'))

        # gets future data
        for i in range(len(list_qb_data) - 1):
            list_qb_data[i] = list_qb_data[i].merge((list_qb_data[i + 1])['fantasy_points_ppr'],
                                                    left_on='espn_id',
                                                    right_on='espn_id',
                                                    suffixes=('', '_n+1'))

        return list_qb_data[3]


    def get_qb_data(self):
        return self.qb_data



    def clean_rb_data(self, year):
        return


    def join_rb_data(self):
        return


    def get_rb_data(self):
        return self.rb_data



    def clean_wr_data(self, year):
        return


    def join_wr_data(self):
        return


    def get_wr_data(self):
        return self.wr_data



    def clean_te_data(self, year):
        return


    def join_te_data(self):
        return


    def get_te_data(self):
        return self.te_data