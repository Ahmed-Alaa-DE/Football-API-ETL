CREATE TABLE SStandings (
[rank] INT NOT NULL, 
team_name NVARCHAR(100) NOT NULL,	
team_id INT NOT NULL PRIMARY KEY,	
points INT NOT NULL,	
goalsDiff INT NOT NULL,	
form NVARCHAR(10),	
[group] NVARCHAR(50) NOT NULL,	
played INT NOT NULL,	
win INT NOT NULL,	
lose INT NOT NULL,	
draw INT NOT NULL,	
goals_for INT NOT NULL,	
goals_against INT NOT NULL
)
