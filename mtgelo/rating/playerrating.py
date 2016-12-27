from mtgelo.scraper.database import *
import trueskill

def testrating():
    conn = connect_db()
    c = conn.cursor()
    create_playerranking()

    c.execute('select * from playerHistory order by coverageid asc, eventid desc, round asc')

    eventdata = c.fetchall()

    playerdata = {}
    for event in eventdata:
        print(event)
        if event[10] != 'TEAM EVENT' or event[14] != 'TEAM EVENT':
            name = event[9].lower() + ' ' + event[10].lower()
            if name not in playerdata:
                playerdata[name] = [trueskill.Rating(), 0]

            opponenet_name = event[13].lower() + ' ' + event[14].lower()
            if opponenet_name not in playerdata:
                playerdata[opponenet_name] = [trueskill.Rating(), 0]

    print("Player Data Length: ", len(playerdata))

    for event in eventdata:
        if event[10] != 'TEAM EVENT' or event[14] != 'TEAM EVENT':
            player_name = event[9].lower() + ' ' + event[10].lower()
            opponenet_name = event[13].lower() + ' ' + event[14].lower()

            if player_name in playerdata and opponenet_name in playerdata:
                player_rating = playerdata[player_name][0]
                opponent_rating = playerdata[opponenet_name][0]
                playerdata[player_name][1] += 1
                playerdata[opponenet_name][1] += 1
                if event[12] == "Won":
                    playerdata[player_name][0], playerdata[opponenet_name][0] = trueskill.rate_1vs1(player_rating, opponent_rating)
                elif event[12] == "Lost":
                    playerdata[opponenet_name][0], playerdata[player_name][0] = trueskill.rate_1vs1(opponent_rating, player_rating)
                elif event[12] == "Drew":
                    playerdata[player_name][0], playerdata[opponenet_name][0] = trueskill.rate_1vs1(player_rating, opponent_rating, drawn=True)
    print(playerdata)

    test = reversed(sorted(playerdata, key=playerdata.get))

    for player in test:
        mtgelo = int(playerdata[player][0].mu * (trueskill.Rating().sigma / playerdata[player][0].sigma) * 10)
        playerRankToDB([player, playerdata[player][0].mu, playerdata[player][0].sigma, playerdata[player][1], mtgelo])
