from mtgelo.scraper.database import *
from mtgelo.scraper.unicode_parser import *
import unicodedata
import difflib

#This is the brute force solution...
#Trying to match every name with every other name...
#Way too slow...
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

    #first get all the name information available
    c.execute('select playerfirstname, playerlastname, opponentfirstname, opponentlastname from playerHistory')
    eventdata = c.fetchall()


    playerdata = {}
    #Then create an object, where we find all people with the same last name, and then compare their first name
    #The idea: Find all people with the same last name
    #and then try to determine if they are the same person, with some typo in their first name.

    #The result is a dictionary, where the value is a set
    #The dictionary key is the Last Name
    #The set ensures that only unique First Names get added
    #End result is an object where we can see all unique first names for a particular last name

    for event in eventdata[10000:]:
        #ignore team events for this exercise
        if event[1] != 'TEAM EVENT' or event[3] != 'TEAM EVENT':
            #normalize people's first and last names
            player_first_name = strip_accents(event[0].lower())
            player_last_name = strip_accents(event[1].lower())
            opponent_first_name = strip_accents(event[2].lower())
            opponent_last_name = strip_accents(event[3].lower())

            #check if player lastname is already in the index
            if player_last_name not in playerdata:
                #if it isn't, create an object where we have a counter, and a set where we will place first names
                playerdata[player_last_name] = [0, set()]
            #then add the first name to the set, and up the counter
            playerdata[player_last_name][1].add(player_first_name)
            playerdata[player_last_name][0] += 1

            #same for opponent names
            if opponent_last_name not in playerdata:
                playerdata[opponent_last_name] = [0, set()]
            playerdata[opponent_last_name][1].add(opponent_first_name)
            playerdata[opponent_last_name][0] += 1

    print(len(playerdata))

    #Then for all the first names that have the same last name, lets find out which ones of them are similar
    #If two first names with the same last name are a close match, we will store them in this array as a sub array
    #the subarray will compose of: the last name the first name shares, the two similar first names, and match percent
    matchlist = []

    for key, value in playerdata.items():
        #for a specific lastname key, if there are more than 1 first names
        if len(value[1]) > 1:
            #take the set of first names, and turn it into an index-able list
            first_name_list = list(value[1])
            length = len(first_name_list)

            #we are going to loop through all the first names, comparing them only to the names after them
            #Every 2 names should be compared at least once this way, without any repeating comparison
            #and without comparing the same element with itself

            #first element is at 0
            i = 0
            while (i < length):
                #compare it to the element starting after it
                j = i + 1
                while(j < length):
                    #compare the two names
                    compare = difflib.SequenceMatcher(None, first_name_list[i], first_name_list[j])
                    #This ratio can be adjusted for more strict and less strict comparison
                    if compare.ratio() > .75:
                        #If the comparison is close, then add new subarray with the relevant values
                        matchlist.append([key, first_name_list[i], first_name_list[j], compare.ratio()])
                    j += 1
                i += 1
    print(len(matchlist))

    #Finally, we want to create "people", where there are multiple matches...
    #For example, if A matches B, and B matches C... then [A,B,C] is probably all the same name for 1 person
    #Although some last names may have 2 people or more represented

    #We will create a dictionary of last names again, where the key is last names
    #The value will be an array of sets
    #Each set will contain the first names of a single 'person'

    # this is where we will store everything in the end
    extended_match = {}

    #look through the list of matches
    for suggestion in matchlist:
        last_name = suggestion[0]
        first_name_1 = suggestion[1]
        first_name_2 = suggestion[2]
        percent_match = suggestion[3]

        #check if the last name is not already a key in the dictionary
        if last_name not in extended_match:
            #if not create an array, where the the first set is created with the two names
            #Then skip to the next loop
            extended_match[last_name] = [set([first_name_1, first_name_2])]
            continue

        #name_block here is the set()
        length = len(extended_match[last_name])
        print("Length: ", length)
        i = 0
        while i < length:
            name_block = extended_match[last_name][i]
            print(name_block, first_name_1, first_name_2)
            #if the name block has half of the match, add the other half
            if first_name_1 in name_block:
                name_block.add(first_name_2)
            elif first_name_2 in name_block:
                name_block.add(first_name_1)
            #If neither name is in the current set, create a new set, and place both names in it
            else:
                print("no match")
                extended_match[last_name].append(set([first_name_1, first_name_2]))
            i += 1
    return extended_match
