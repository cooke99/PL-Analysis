import pandas as pd
import numpy as np

def convert_points(position: str, GW_data: pd.DataFrame) -> pd.DataFrame:
    '''
    Takes a DataFrame of FPL GW data, and maps the statistics to the corresponding
    points scored.
    
    Inputs:
    -------
        position (str) : 'GK', 'DEF', 'MID', 'FWD' are the options.
        GW_data (pd.DataFrame) : Dataframe of FPL GW data.
        
    Outputs:
    --------
        points_data (pd.DataFrame) : A copy of GW_data with the FPL stats mapped to points.
    '''
    
    GK_points = {'< 60 mins':1, '>= 60 mins':2, 'goal':6, 'assist':3, 
                 'clean sheet':4, '3 shots saved':1, 'penalty saved':5,
                'penalty miss':-2, '2 goals conceded':-1, 'yellow card':-1,
                'red card':-3, 'own goal':-2}
    
    DEF_points = {'< 60 mins':1, '>= 60 mins':2, 'goal':6, 'assist':3, 
                 'clean sheet':4, '3 shots saved':0, 'penalty saved':0,
                'penalty miss':-2, '2 goals conceded':-1, 'yellow card':-1,
                'red card':-3, 'own goal':-2}
    
    MID_points = {'< 60 mins':1, '>= 60 mins':2, 'goal':5, 'assist':3, 
                 'clean sheet':1, '3 shots saved':0, 'penalty saved':0,
                'penalty miss':-2, '2 goals conceded':0, 'yellow card':-1,
                'red card':-3, 'own goal':-2}
    
    FWD_points = {'< 60 mins':1, '>= 60 mins':2, 'goal':4, 'assist':3, 
                 'clean sheet':0, '3 shots saved':0, 'penalty saved':0,
                'penalty miss':-2, '2 goals conceded':0, 'yellow card':-1,
                'red card':-3, 'own goal':-2}
    
    points = {'GK': GK_points, 'DEF': DEF_points, 'MID': MID_points,
             'FWD': FWD_points}
    
    points_data = GW_data.copy()
    
    points_data.minutes = np.where((points_data.minutes < 60) & (points_data.minutes > 0), 
                                   points[position]['< 60 mins'], points_data.minutes)
    points_data.minutes = np.where(points_data.minutes >= 60, points[position]['>= 60 mins'], points_data.minutes)
    points_data.goals_scored = points_data.goals_scored*points[position]['goal']
    points_data.assists = points_data.assists*points[position]['assist']
    points_data.clean_sheets = points_data.clean_sheets*points[position]['clean sheet']
    points_data.saves = (points_data.saves // 3)*points[position]['3 shots saved']
    points_data.penalties_saved = points_data.penalties_saved*points[position]['penalty saved']
    points_data.penalties_missed = (points_data.penalties_missed)*points[position]['penalty miss']
    points_data.goals_conceded = (points_data.goals_conceded // 2)*points[position]['2 goals conceded']
    points_data.yellow_cards = (points_data.yellow_cards)*points[position]['yellow card']
    points_data.red_cards = (points_data.red_cards)*points[position]['red card']
    points_data.own_goals = (points_data.own_goals)*points[position]['own goal']
    
    return points_data