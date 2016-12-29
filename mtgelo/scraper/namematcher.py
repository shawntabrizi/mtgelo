from mtgelo.scraper.database import *
from mtgelo.scraper.unicode_parser import *
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

def lastnamematch():
    conn = connect_db()
    c = conn.cursor()

    c.execute('select playerfirstname, playerlastname, opponentfirstname, opponentlastname from playerHistory')

    eventdata = c.fetchall()

    playerdata = {}
    for event in eventdata:
        #print(event)
        if event[1] != 'TEAM EVENT' or event[3] != 'TEAM EVENT':
            player_first_name = strip_accents(event[0].lower())
            player_last_name = strip_accents(event[1].lower())
            opponent_first_name = strip_accents(event[2].lower())
            opponent_last_name = strip_accents(event[3].lower())

            if player_last_name not in playerdata:
                playerdata[player_last_name] = [0, set()]
            playerdata[player_last_name][1].add(player_first_name)
            playerdata[player_last_name][0] += 1

            if opponent_last_name not in playerdata:
                playerdata[opponent_last_name] = [0, set()]
            playerdata[opponent_last_name][1].add(opponent_first_name)
            playerdata[opponent_last_name][0] += 1

    print(len(playerdata))

    matchlist = []

    for key, value in playerdata.items():
        if len(value[1]) > 1:
            first_name_list = list(value[1])
            length = len(first_name_list)
            i = 0
            while (i < length):
                j = i + 1
                while(j < length):
                    compare = difflib.SequenceMatcher(None, first_name_list[i], first_name_list[j])
                    if compare.ratio() > .75:
                        matchlist.append([key, first_name_list[i], first_name_list[j], compare.ratio()])
                    j += 1
                i += 1
    print(len(matchlist))
    return matchlist
