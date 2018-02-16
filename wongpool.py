from __future__ import print_function
from collections import defaultdict
import mlbgame
hml=[]
with open ("players", "r") as myfile:
    data = myfile.readlines()
plist=[]
for line in data:
    cspot=line.find(",")
    plist.append(line[cspot+2:25].rstrip()+" "+line[5:cspot])
for m in range(4,5):
    print(m)
    month = mlbgame.games(2017, m)
    mc = m
    if mc==3:
        mc=4
    if mc==10:
        mc=9
    games=mlbgame.combine_games(month)
    olddate=""
    hr=0
    for game in games:
        date=game.game_id[0:10]
        if date<>olddate:
            olddate=date
            print(date,hr)
            hr=0
        try:
            if mlbgame.overview(game.game_id).game_type=="R":
                stats = mlbgame.player_stats(game.game_id)
                for player in stats.home_batting:
                    if (player.name_display_first_last in plist) and player.hr>0:
                        print(player.name_display_first_last)
                        hml.append([str(mc)+" "+player.name_display_first_last,player.hr])
                        hr=hr+player.hr
                for player in stats.away_batting:
                    if (player.name_display_first_last in plist) and player.hr>0:
                        hml.append([str(mc)+" "+player.name_display_first_last,player.hr])
                        hr=hr+player.hr
        except ValueError:
            pass
result = defaultdict(int)
for n,h in hml:
    result[n] += h
result = result.items()

s = [[str(e) for e in row] for row in result]
lens = [max(map(len, col)) for col in zip(*s)]
fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
table = [fmt.format(*row) for row in s]
print('\n'.join(table))












