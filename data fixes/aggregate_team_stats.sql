SELECT goals_scored.team_name AS team_name, strength, strength_overall_home, strength_overall_away, strength_attack_home, strength_attack_away, strength_defence_home, strength_defence_away, total_goals_scored, total_home_goals, total_away_goals, total_goals_conceded, total_home_goals_conceded, total_away_goals_conceded FROM (SELECT home_team AS team_name, total_away_goals + total_home_goals AS total_goals_scored, total_home_goals, total_away_goals FROM (SELECT teams1.name AS away_team, SUM(team_a_score) AS total_away_goals FROM fixtures 
LEFT JOIN (SELECT id, name FROM teams) AS teams1
ON fixtures.team_a = teams1.id
GROUP BY teams1.name
ORDER BY away_team) AS away_goals
LEFT JOIN (SELECT teams2.name AS home_team, SUM(team_h_score) AS total_home_goals FROM fixtures
LEFT JOIN (SELECT id, name FROM teams) AS teams2
ON fixtures.team_h = teams2.id
GROUP BY teams2.name
ORDER BY home_team) AS home_goals
ON away_goals.away_team = home_goals.home_team) AS goals_scored
LEFT JOIN (SELECT home_team AS team_name, total_away_goals_conceded + total_home_goals_conceded AS total_goals_conceded, total_away_goals_conceded, total_home_goals_conceded FROM (SELECT teams1.name AS away_team, SUM(team_h_score) AS total_away_goals_conceded FROM fixtures 
LEFT JOIN (SELECT id, name FROM teams) AS teams1
ON fixtures.team_a = teams1.id
GROUP BY teams1.name
ORDER BY away_team) AS away_goals_conceded
LEFT JOIN (SELECT teams2.name AS home_team, SUM(team_a_score) AS total_home_goals_conceded FROM fixtures
LEFT JOIN (SELECT id, name FROM teams) AS teams2
ON fixtures.team_h = teams2.id
GROUP BY teams2.name
ORDER BY home_team) AS home_goals_conceded
ON away_goals_conceded.away_team = home_goals_conceded.home_team
ORDER BY total_goals_conceded DESC) AS goals_conceded
ON goals_scored.team_name = goals_conceded.team_name
LEFT JOIN teams
ON goals_scored.team_name = teams.name;