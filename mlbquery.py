import cfg

def hrthisday(plist,daystring):
#    returns a list of homers hit on a particular day by players in the list players
#    fullname, gameid, hrshit
    from collections import defaultdict
    import mlbgame
    hml=[]
    month = mlbgame.games(2017, months=int(daystring[0:2]),days=int(daystring[3:5]))
    mc = int(daystring[0:2])
    if mc==3:
        mc=4
    if mc==10:
        mc=9
    games=mlbgame.combine_games(month)
    for game in games:
        date=game.game_id[0:10]
        try:
            if mlbgame.overview(game.game_id).game_type=="R":
                stats = mlbgame.player_stats(game.game_id)
                for player in stats.home_batting:
                    if ((player.name_display_first_last in plist) or plist==[]) and player.hr>0:
                        hml.append([player.name_display_first_last,game.game_id,player.hr])
                for player in stats.away_batting:
                    if ((player.name_display_first_last in plist) or plist==[]) and player.hr>0:
                        hml.append([player.name_display_first_last,game.game_id,player.hr])
        except ValueError:
            pass
    return hml

    #s = [[str(e) for e in row] for row in result]
    #lens = [max(map(len, col)) for col in zip(*s)]
    #fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    #table = [fmt.format(*row) for row in s]
    #print '\n'.join(table)



#print hrthisday(plist,"07/07")











