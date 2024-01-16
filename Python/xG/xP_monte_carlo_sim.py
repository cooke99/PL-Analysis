"""
Monte-Carlo simulation to generate expected points (xP) from expected goals
data (xG). Data taken from "The Expected Goals Philosophy". Based on a 2019 fixture
between Arsenal and Manchester United which saw ARS accumulate 1.53 xG and MU 2.37 xG.
Despite the xG scoreline, ARS won 2 - 0.
"""

import numpy as np

NUM_SIMS = 100000 # Number of simulations.
WIN_PTS = 3 # Points assigned by Premier League for a win
DRAW_PTS = 1 # Points assigned by Premier League for a draw
LOSE_PTS = 0 # " loss

# Individual xG of all shots taken by Arsenal & Manchester United:
ARS_xG = [0.02,0.02,0.03,0.04,0.04,0.05,0.06,0.07,0.09,0.1,0.12,0.13,0.76] 
MU_xG = [0.01,0.02,0.02,0.02,0.03,0.05,0.05,0.05,0.06,0.22,0.3,0.43,0.48,0.63]

# Track total points gained by each team over all the simulations:
ARS_pts = 0
MU_pts = 0

for i in range(NUM_SIMS):
    ARS_goals = 0
    MU_goals = 0
    for shot in ARS_xG:
        # For each shot on goal, we draw from a binomial distribution with 1 trial
        # and probability of success given by the xG of the shot (same as probability of a goal
        # from that shot) If the sample is a success, then the shot resulted in a goal
        # for this simulated match. We sum the goals scored by each side for this "match".
        ARS_goals += int(np.random.binomial(1,shot,None))
        
    for shot in MU_xG:
        MU_goals += int(np.random.binomial(1,shot,None))
        
    # Determine who won this simulated match and assign resulting points:
    if ARS_goals > MU_goals:
        # ARS win
        ARS_pts += WIN_PTS
        
    elif ARS_goals < MU_goals:
        # MU win
        MU_pts += WIN_PTS
        
    else:
        # Draw
        ARS_pts += DRAW_PTS
        MU_pts += DRAW_PTS
        
ARS_xP = ARS_pts/NUM_SIMS
MU_xP = MU_pts/NUM_SIMS

print(f'Arsenal xP: {ARS_xP}\nManchester United xP: {MU_xP}')