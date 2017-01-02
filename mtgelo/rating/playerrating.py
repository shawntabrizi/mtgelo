from mtgelo.scraper.database import *
from mtgelo.scraper.unicode_parser import *
import trueskill
import re


def player_rating_from_db():
    conn = connect_db()
    c = conn.cursor()

    #this will delete DB data, and recreate it...
    create_playerranking()

    c.execute('select * from playerHistory order by coverageid asc, eventid desc, round asc')

    eventdata = c.fetchall()

    playerdata = {}
    for event in eventdata:
        #print(event)
        if event[10] != 'team event' and event[14] != 'team event' and event[10] != 'bye' and event[14] != 'bye' and event[12] != '':
            name = event[9] + ' ' + event[10]
            name = strip_accents(name)

            if name not in playerdata:
                playerdata[name] = [trueskill.Rating(), 0]

            opponent_name = event[13] + ' ' + event[14]
            opponent_name = strip_accents(opponent_name)
            if opponent_name not in playerdata:
                playerdata[opponent_name] = [trueskill.Rating(), 0]

    print("Player Data Length: ", len(playerdata))

    for event in eventdata:
        if event[10] != 'team event' and event[14] != 'team event' and event[10] != 'bye' and event[14] != 'bye' and event[12] != '':
            player_name = event[9] + ' ' + event[10]
            opponent_name = event[13] + ' ' + event[14]

            player_name = strip_accents(player_name)
            opponent_name = strip_accents(opponent_name)

            if player_name in playerdata and opponent_name in playerdata:
                player_rating = playerdata[player_name][0]
                opponent_rating = playerdata[opponent_name][0]
                playerdata[player_name][1] += 1
                playerdata[opponent_name][1] += 1
                if event[12] == "won":
                    playerdata[player_name][0], playerdata[opponent_name][0] = trueskill.rate_1vs1(player_rating, opponent_rating)
                elif event[12] == "lost":
                    playerdata[opponent_name][0], playerdata[player_name][0] = trueskill.rate_1vs1(opponent_rating, player_rating)
                elif event[12] == "drew":
                    playerdata[player_name][0], playerdata[opponent_name][0] = trueskill.rate_1vs1(player_rating, opponent_rating, drawn=True)
    print(playerdata)

    player_db = []

    for player in playerdata:
        #This is BS rating forumla
        mtgelo = int(playerdata[player][0].mu * (trueskill.Rating().sigma / playerdata[player][0].sigma) * 10)
        tsrating = playerdata[player][0].mu - 3 * playerdata[player][0].sigma
        player_db.append([player, playerdata[player][0].mu, playerdata[player][0].sigma, playerdata[player][1], mtgelo, tsrating])

    playerRankToDB(player_db)
