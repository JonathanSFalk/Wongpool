import cfg
import mlbgame
"2018_03_21_sdnmlb_chamlb_1"
stats = mlbgame.player_stats("2018_03_21_sdnmlb_chamlb_1")
for player in stats.home_batting:
    attributes = [i for i in player.__dict__.keys() if i[0:2] != "__"]
    for a in attributes:
        print(a,player.__dict__[a])
    print("")






