import .database
import trueskill

def testrating():
    conn = connect_db()
    c = conn.cursor()

    c.execute('select * from playerHistory')

    eventdata = c.fetchall()

    print (eventdata)
    playerdata = {}
    for event in eventdata:
        name = event[9] + ' ' + event[10]
        if name not in playerdata:
            playerdata[name] = trueskill.Rating()

        opponenet_name = event[13] + ' ' + event[14]
        if opponenet_name not in playerdata:
            playerdata[opponenet_name] = trueskill.Rating()

    for event in eventdata:
        if True:
            player_name = event[9] + ' ' + event[10]
            opponenet_name = event[13] + ' ' + event[14]
            #if("Tomelitsch" in player_name or "Tomelitsch" in opponenet_name):
                #print(player_name, opponenet_name)

            if player_name in playerdata and opponenet_name in playerdata:
                player_rating = playerdata[player_name]
                opponent_rating = playerdata[opponenet_name]
                if event[12] == "Won":
                    playerdata[player_name], playerdata[opponenet_name] = trueskill.rate_1vs1(player_rating, opponent_rating)
                elif event[12] == "Lost":
                    playerdata[opponenet_name], playerdata[player_name] = trueskill.rate_1vs1(opponent_rating, player_rating)
                elif event[12] == "Drew":
                    playerdata[player_name], playerdata[opponenet_name] = trueskill.rate_1vs1(player_rating, opponent_rating, drawn=True)
    print(playerdata)

    test = sorted(playerdata, key=playerdata.get)

    for player in test:
        print(player, playerdata[player])
    # print (len(playerdata), playerdata)
    #
    # playerset = [list(t) for t in set(tuple(element) for element in playerdata)]
    # for player in playerset:
    #     player.append(trueskill.Rating())
    # print (len(playerset), playerset)

    return playerdata