from mtgelo.scraper.database import *
from mtgelo.scraper.unicode_parser import *
import unicodedata
import difflib
import sys
import csv

compare_ratio = .75

#This is the brute force solution...
#Trying to match every name with every other name... where the first two letters match
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

#find similar first names, when the last name matches
#I can probably optimize to remove the last loop, and stick it into the loop beforehand
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

    for event in eventdata:
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
                    if compare.ratio() > compare_ratio:
                        #If the comparison is close, then add new subarray with the relevant values
                        matchlist.append([key, first_name_list[i], first_name_list[j], compare.ratio()])
                    j += 1
                i += 1
    print(len(matchlist))

    with open("output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(matchlist)

    #Finally, we want to create "people", where there are multiple matches...
    #For example, if A matches B, and B matches C... then [A,B,C] is probably all the same name for 1 person
    #Although some last names may have 2 people or more represented

    #We will create a dictionary of last names again, where the key is last names
    #The value will be an array of sets
    #Each set will contain the first names of a single 'person'

    # this is where we will store everything in the end
    extended_match = {}

    #look through the list of matches
    for suggestion in matchlist[10:]:
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


        length = len(extended_match[last_name])
        print("Length: ", length)
        found = False
        # name_block here is the set()
        for name_block in extended_match[last_name]:
            print(name_block, first_name_1, first_name_2)
            #if the name block has half of the match, add the other half
            if first_name_1 in name_block:
                name_block.add(first_name_2)
                found = True
                break
            elif first_name_2 in name_block:
                name_block.add(first_name_1)
                found = True
                break
        #If neither name is in the current set, create a new set, and place both names in it
        if not found:
            extended_match[last_name].append(set([first_name_1, first_name_2]))

    return extended_match

#find similar last names, when the first name matches
#note this is a copy paste from the script above... maybe has bugs
#I can probably optimize to remove the last loop, and stick it into the loop beforehand
def firstnamematch():
    conn = connect_db()
    c = conn.cursor()

    #last get all the name information available
    c.execute('select playerfirstname, playerlastname, opponentfirstname, opponentlastname from playerHistory')
    eventdata = c.fetchall()


    playerdata = {}
    #Then create an object, where we find all people with the same first name, and then compare their last name
    #The idea: Find all people with the same first name
    #and then try to determine if they are the same person, with some typo in their last name.

    #The result is a dictionary, where the value is a set
    #The dictionary key is the first Name
    #The set ensures that only unique last Names get added
    #End result is an object where we can see all unique last names for a particular first name

    for event in eventdata:
        #ignore team events for this exercise
        if event[1] != 'TEAM EVENT' or event[3] != 'TEAM EVENT':
            #normalize people's last and first names
            player_first_name = strip_accents(event[0].lower())
            player_last_name = strip_accents(event[1].lower())
            opponent_first_name = strip_accents(event[2].lower())
            opponent_last_name = strip_accents(event[3].lower())

            #check if player firstname is already in the index
            if player_first_name not in playerdata:
                #if it isn't, create an object where we have a counter, and a set where we will place last names
                playerdata[player_first_name] = [0, set()]
            #then add the last name to the set, and up the counter
            playerdata[player_first_name][1].add(player_last_name)
            playerdata[player_first_name][0] += 1

            #same for opponent names
            if opponent_first_name not in playerdata:
                playerdata[opponent_first_name] = [0, set()]
            playerdata[opponent_first_name][1].add(opponent_last_name)
            playerdata[opponent_first_name][0] += 1

    print(len(playerdata))

    #Then for all the last names that have the same first name, lets find out which ones of them are similar
    #If two last names with the same first name are a close match, we will store them in this array as a sub array
    #the subarray will compose of: the first name the last name shares, the two similar last names, and match percent
    matchlist = []

    for key, value in playerdata.items():
        #for a specific firstname key, if there are more than 1 last names
        if len(value[1]) > 1:
            #take the set of last names, and turn it into an index-able list
            last_name_list = list(value[1])
            length = len(last_name_list)

            #we are going to loop through all the last names, comparing them only to the names after them
            #Every 2 names should be compared at least once this way, without any repeating comparison
            #and without comparing the same element with itself

            #last element is at 0
            i = 0
            while (i < length):
                #compare it to the element starting after it
                j = i + 1
                while(j < length):
                    #compare the two names
                    compare = difflib.SequenceMatcher(None, last_name_list[i], last_name_list[j])
                    #This ratio can be adjusted for more strict and less strict comparison
                    if compare.ratio() > compare_ratio:
                        #If the comparison is close, then add new subarray with the relevant values
                        matchlist.append([key, last_name_list[i], last_name_list[j], compare.ratio()])
                    j += 1
                i += 1
    print(len(matchlist))

    #Finally, we want to create "people", where there are multiple matches...
    #For example, if A matches B, and B matches C... then [A,B,C] is probably all the same name for 1 person
    #Although some first names may have 2 people or more represented

    #We will create a dictionary of first names again, where the key is first names
    #The value will be an array of sets
    #Each set will contain the last names of a single 'person'

    # this is where we will store everything in the end
    extended_match = {}

    #look through the list of matches
    for suggestion in matchlist[10:]:
        first_name = suggestion[0]
        last_name_1 = suggestion[1]
        last_name_2 = suggestion[2]
        percent_match = suggestion[3]

        #check if the first name is not already a key in the dictionary
        if first_name not in extended_match:
            #if not create an array, where the the last set is created with the two names
            #Then skip to the next loop
            extended_match[first_name] = [set([last_name_1, last_name_2])]
            continue


        length = len(extended_match[first_name])
        print("Length: ", length)
        found = False
        # name_block here is the set()
        for name_block in extended_match[first_name]:
            print(name_block, last_name_1, last_name_2)
            #if the name block has half of the match, add the other half
            if last_name_1 in name_block:
                name_block.add(last_name_2)
                found = True
                break
            elif last_name_2 in name_block:
                name_block.add(last_name_1)
                found = True
                break
        #If neither name is in the current set, create a new set, and place both names in it
        if not found:
            extended_match[first_name].append(set([last_name_1, last_name_2]))

    return extended_match


def create_update_query_last_name():
    #first get all the suggested changes
    changes = lastnamematch()
    #We will create a text file with all the DB updates
    f = open('update_query_last_name.txt', 'w')

    #create the changes as lines of SQLite queries
    for key, value in changes.items():
        #Key is last name, value is an array of sets of first names
        for group in value:
            line_string = ''
            #find the longest name in the set, which we assume is the correct name
            max_name = max(group, key=len)
            #remove this name from the set of data we will change, since it is already correct
            group.remove(max_name)
            #beggining of the query updates the table, and sets the first name to the name we want, where last name
            #matches the name we are looking for
            line_string = 'update playerHistory set playerfirstname = "' + max_name + '" where playerlastname = "' + key + '" and ('
            #and where the existing first name is one of the names in the group
            for name in group:
                line_string += 'playerfirstname = "' + name + '" or '
            #remove last 4 characters which should be ' or '
            line_string = line_string[:-4]
            line_string += ')\n'
            f.write(line_string)
    f.close()
