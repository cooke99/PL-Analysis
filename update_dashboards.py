import os
import numpy as np
import pandas as pd
from scipy.stats import *
from statsmodels.stats.multitest import multipletests
from convert_points import convert_points

def update_dashboards(position: str = 'DEF', top_n: int = 20) -> None:
    """
    Update the data CSVs that are used by Tableau to generate
    the dashboards. We are now using only 2021 - 2023 data
    to compare with this season (2023/24).

    Parameters
    ----------
    position : str, optional
        Specify which dashboard to update. Options
        are 'GK', 'DEF', 'MID', 'FWD'. The default 
        is 'DEF'.
    top_n : int, optional
        How many players to include in the results table. Usually
        pick 10 for GK, 15 for FWD and 20 for DEF/MID. The default 
        is 20.

    Returns
    -------
    None
        DESCRIPTION.
        
    """
    
    if not(position in ['GK','DEF','MID','FWD']):
        raise Exception('Invalid position specified.\nMust be one of: GK, DEF, MID, FWD.')
    
    # Load 2023/24 season data
    path_2023_24 = '../data/Fantasy-Premier-League/data/2023-24/gws/merged_gw.csv'
    data_2023_24 = pd.read_csv(path_2023_24, low_memory = False)
    data_2023_24.loc[:,'total - bonus points'] = data_2023_24.total_points - data_2023_24.bonus
    data_2023_24.loc[:,'position'] = data_2023_24.position.map({'DEF':'DEF','FWD':'FWD','GK':'GK','GKP':'GK','MID':'MID'}) # Fix any incorrect position labels
    latest_prices = data_2023_24.loc[:,['GW','name','value']].copy()
    data_2023_24 = data_2023_24.loc[data_2023_24.minutes > 0, :] # We're only going to look at appearances.
    POS_2023_24 = data_2023_24.loc[data_2023_24.position == position, 'name'].unique()

    if not(os.path.exists(f'./results/{position}_data_2021_2023.csv')):
        # If a data file doesn't already exist, we need to load the 2021 - 2023
        # data and rank according to the highest mean pts per appearance.
        data_2021_23_path = '../data/Fantasy-Premier-League/data/cleaned_merged_seasons.csv'
        seasons_df = pd.read_csv(data_2021_23_path, low_memory = False)
        seasons = ['2021-22', '2022-23']
        data_2021_23_df = seasons_df.loc[seasons_df.season_x.isin(seasons),:]
        data_2021_23_df.loc[:,'position'] = data_2021_23_df.position.map({'DEF':'DEF','FWD':'FWD','GK':'GK','GKP':'GK','MID':'MID'})
        POS_2021_23_data = data_2021_23_df.loc[data_2021_23_df.name.isin(POS_2023_24),:]
        POS_2021_23_data.loc[:,'total - bonus points'] = POS_2021_23_data.total_points - POS_2021_23_data.bonus
        POS_2021_23_data = POS_2021_23_data.loc[POS_2021_23_data.minutes > 0, :]
        
        # Remap the points (following method detailed in notebooks):
        Remap_POS_2021_2023 = POS_2021_23_data.loc[:, ['name', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'saves',
                                                       'penalties_saved', 'penalties_missed', 'goals_conceded', 'yellow_cards',
                                                       'red_cards', 'own_goals']]
        Remap_POS_2021_2023 = convert_points(position, Remap_POS_2021_2023)
        Remap_POS_2021_2023['total - bonus points'] =  Remap_POS_2021_2023.drop(columns=['name']).sum(axis=1)
        
        # Calculate mean pts/appearance:
        top_n_mean = Remap_POS_2021_2023.loc[:, ['name','total - bonus points']].groupby(['name']).mean()
        top_n_mean.sort_values(by='total - bonus points',ascending=False,inplace=True)
        top_n_mean = top_n_mean.iloc[0:top_n]
        top_n_mean = top_n_mean.rename(columns={'total - bonus points':'mean total - bonus 2021 - 2023'})
        top_n_names = list(top_n_mean.index)
        
        # How many appearances did they have in these 2 seasons?
        matches_played = POS_2021_23_data.loc[:,['name','GW']].groupby('name').size()
        matches_played = matches_played.loc[top_n_names]
        matches_played.name = 'Appearances 2021-2023'
        top_n_mean = top_n_mean.join(matches_played)
        top_n_mean = top_n_mean[['Appearances 2021-2023', 'mean total - bonus 2021 - 2023']]
        
        # Calculate std:
        pts_std = Remap_POS_2021_2023.loc[:,['name','total - bonus points']].groupby(['name']).std()
        pts_std.rename(columns = {'total - bonus points':'Std total - bonus 2021 - 2023'},inplace = True)
        top_n_mean = top_n_mean.join(pts_std, how='left')
        top_n_mean.to_csv(f'./results/{position}_data_2021_2023.csv')
        
    else:
        top_n_mean = pd.read_csv(f'./results/{position}_data_2021_2023.csv', index_col = 'name')
        
    # Update file with latest 2023/24 season data:
    mean_pts_2023_24 = data_2023_24.loc[data_2023_24.name.isin(top_n_names),['name',\
                                    'total - bonus points']].groupby(['name']).mean()
    mean_pts_2023_24.rename(columns={'total - bonus points':'mean total - bonus 2023-24'}, inplace = True)
    top_n_mean = top_n_mean.join(mean_pts_2023_24, how = 'left')
    
    # Calculate effect size with Cohen's d:
    top_n_mean['Effect size'] = (top_n_mean['mean total - bonus 2023-24'] - \
                                 top_n_mean['mean total - bonus 2021 - 2023'])\
                                /top_n_mean['Std total - bonus 2021 - 2023']
    
    # Calculate appearances in 2023/24 season:
    apps_2023_24 = data_2023_24.loc[data_2023_24.name.isin(top_n_names),['name',\
                                    'GW']].groupby(['name']).size()
    apps_2023_24.name = 'Appearances 2023-24'
    top_n_mean = top_n_mean.join(apps_2023_24, how = 'left')
    
    # 1-sided t-test to deteermine if there is a statistically significant change
    # in performance. Use appearances as sample size N.
    # H0 : mean points 2023/24 season - mean points 2021/22 - 2022/23 = 0
    # HA : mean points 2023/24 season > mean points 2021/22 - 2022/23 **OR** 
    #      mean points 2023/24 season < mean points 2021/22 - 2022/23
    #      (depending on the change)
    top_n_mean['SE'] = top_n_mean['Std total - bonus 2021 - 2023']/np.sqrt(top_n_mean['Appearances 2023-24'])
    top_n_mean['t'] = (top_n_mean['mean total - bonus 2023-24'] - \
                       top_n_mean['mean total - bonus 2021 - 2023'])/top_n_mean['SE']
    top_n_mean['p-value'] = t.sf(np.abs(top_n_mean['t'].values), top_n_mean['Appearances 2023-24'].values-1)
    
    # Apply Benjamini-Hochberg procedure to control FDR to 5%:
    top_n_mean['BH Stat Signf'], _, _, _ = multipletests(top_n_mean['p-value'].values, 
                                                         alpha=0.05, 
                                                         method='fdr_bh',
                                                         is_sorted=False, 
                                                         returnsorted=False)
    
    # Effect size label:
    top_n_mean['Effect size label'] = np.digitize(np.abs(top_n_mean['Effect size']), [0.01,0.2,0.5,0.8,1.20,2.0],
                                                   right = True)
    top_n_mean['Effect size label'] = top_n_mean['Effect size label'].map({0:'None',1:'Very small',2:'Small',
                                                                           3:'Medium',4:'Large',5:'Very large',
                                                                           6:'Huge'})
    
    # Add price column:
    latest_GW = latest_prices.GW.max()
    latest_prices = latest_prices.loc[(latest_prices.GW == latest_GW) & (latest_prices.name.isin(top_n_names)), 
                                    ['name','value']]
    latest_prices.set_index('name',inplace=True)
    latest_prices.value /= 10 # get price in millions
    latest_prices.rename(columns={'value':'Current Price (M)'}, inplace=True)
    top_n_mean = top_n_mean.join(latest_prices, how='left')
    
    # Add mean opposition strength (using FDR for simplicity):
    team_data_path = '../data/Fantasy-Premier-League/data/2023-24/teams.csv'
    team_data = pd.read_csv(team_data_path)
    team_id_rank_map = dict(zip(team_data.id, team_data.strength)) # Create map between team id and strength
    
    avg_team_rank = data_2023_24.loc[data_2023_24.name.isin(top_n_names), ['name','opponent_team']]
    avg_team_rank.opponent_team = avg_team_rank.opponent_team.map(team_id_rank_map)
    avg_team_rank = avg_team_rank.groupby('name').mean()
    avg_team_rank.rename(columns = {'opponent_team': 'Average opposition strength 2023-24'}, inplace=True)
    top_n_mean = top_n_mean.join(avg_team_rank, how='left')
    
    # Re-order columns:
    top_n_mean = top_n_mean[['Appearances 2021-2023','mean total - bonus 2021 - 2023',
                             'Std total - bonus 2021 - 2023',
                             'Appearances 2023-24', 'mean total - bonus 2023-24',
                             'Effect size', 'SE','t','p-value','BH Stat Signf',
                             'Effect size label','Current Price (M)','Average opposition strength 2023-24']]
    
    print(top_n_mean)
    top_n_mean.to_csv(f'./results/{position}_data_2023_24.csv')
    return None

if __name__ == '__main__':
    update_dashboards('GK',15)
    update_dashboards('DEF',30)
    update_dashboards('MID',30)
    update_dashboards('FWD',30)
    