from mtgelo.scraper.database import *
import difflib


def namematcher():
    conn = connect_db()
    c = conn.cursor()

    c.execute('select playername from playerRank')

    players = c.fetchall()
    players.sort()

    print(players)

    matchlist = []

    i = 0
    while i < len(players):
        j = i+1
        #only when first letter matches
        print(players[i][0][0], players[j][0][0])
        while j < len(players) and players[i][0][0] == players[j][0][0] and len(players[i][0]) > 1 and len(players[j][0]) > 1 and players[i][0][1] == players[j][0][1]:
            print("Comparing: ", i, players[i][0], j, players[j][0])
            s = difflib.SequenceMatcher(None, players[i][0], players[j][0])
            if .6 <= s.ratio():
                print(i, players[i][0], j, players[j][0])
                matchlist.append([i, players[i][0], j, players[j][0]])
            j += 1
        i += 1
    return matchlist