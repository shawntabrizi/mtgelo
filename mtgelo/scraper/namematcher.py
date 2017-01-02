from mtgelo.scraper.database import *
from mtgelo.scraper.unicode_parser import *
from string import ascii_lowercase
import unicodedata
import difflib
import sys
import csv

compare_ratio = .85

#find similar first names, when the last name matches
#I can probably optimize to remove the last loop, and stick it into the loop beforehand
def lastnamematch():
    conn = connect_db()
    c = conn.cursor()

    #first get all the name information available
    c.execute('select playerfirstname, playerlastname, opponentfirstname, opponentlastname from playerHistory')
    eventdata = c.fetchall()

    # Then create an object, where we find all people with the same last name, and then compare their first name
    playerdata = unique_primary_name(eventdata)
    print(len(playerdata))

    # Then for all the first names that have the same last name, lets find out which ones of them are similar
    matchlist = match_primary_name(playerdata, compare_ratio)
    print(len(matchlist))


    with open("output.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(matchlist)

def unique_primary_name(eventdata):
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
        if event[1] != 'team event' and event[3] != 'team event':
            #normalize people's first and last names
            player_first_name = strip_accents(event[0].lower())
            player_last_name = strip_accents(event[1].lower())
            opponent_first_name = strip_accents(event[2].lower())
            opponent_last_name = strip_accents(event[3].lower())

            #check if player last name is already in the index
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

    return playerdata


def match_primary_name(playerdata, ratio):
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
                    if compare.ratio() > ratio:
                        #If the comparison is close, then add new subarray with the relevant values, and True
                        matchlist.append([key, first_name_list[i], first_name_list[j], compare.ratio(), True])
                    elif compare.ratio() > ratio - .2:
                        #with False, which signifies to ignore this
                        matchlist.append([key, first_name_list[i], first_name_list[j], compare.ratio(), False])
                    j += 1
                i += 1

    #additional fixes... adjusting the Bool
    for match in matchlist:
        #check make sure first letter matches on both names...
        #this mostly catches bad stuff like: bryan -> ryan, kevin -> devin, adrian dorian
        #we dont want to make these changes
        #if we remove it... no need to check further... just continue

        #First check for names where initial is in the front, and remove it
        if re.search('^[a-zA-Z][\.|\s]', match[1]):
            name_1 = re.sub('^[a-zA-Z][\.|\s]', '', match[1])
        else:
            name_1 = match[1]
        if re.search('^[a-zA-Z][\.|\s]', match[2]):
            name_2 = re.sub('^[a-zA-Z][\.|\s]', '', match[2])
        else:
            name_2 = match[2]
        if match[4] is True and len(name_1) > 0 and len(name_2) > 0 and name_1[0] != name_2[0]:
            print('Removing:: ', match[1], match[2])
            match[4] = False
            continue
        # check if uniquely identifying initials can be used to separate names
        if match[4] is True and re.search(r'\b([a-zA-Z][a-zA-Z]?)\b', match[1]) and re.search(r'\b([a-zA-Z][a-zA-Z]?)\b', match[2]):
            #get the middle initial, only the letters, in lowercase
            mi_1 = re.search(r'\b([a-zA-Z][a-zA-Z]?)\b', match[1]).group(1).lower()
            mi_2 = re.search(r'\b([a-zA-Z][a-zA-Z]?)\b', match[2]).group(1).lower()
            #if the middle intial doesnt match, then it is good
            if mi_1 != mi_2:
                match[4] = False

    return matchlist


def personify_match_list(matchlist):
    # Finally, we want to create "people", where there are multiple matches...
    # For example, if A matches B, and B matches C... then [A,B,C] is probably all the same name for 1 person
    # Although some last names may have 2 people or more represented

    # We will create a dictionary of last names again, where the key is last names
    # The value will be an array of sets
    # Each set will contain the first names of a single 'person'

    # this is where we will store everything in the end
    extended_match = {}

    # look through the list of matches
    for suggestion in matchlist:
        last_name = suggestion[0]
        first_name_1 = suggestion[1]
        first_name_2 = suggestion[2]
        percent_match = float(suggestion[3])
        use_value = bool(suggestion[4])
        if use_value is True:
            # check if the last name is not already a key in the dictionary
            if last_name not in extended_match:
                # if not create an array, where the the first set is created with the two names
                # Then skip to the next loop
                extended_match[last_name] = [set([first_name_1, first_name_2])]
                continue

            found = False
            # name_block here is the set()
            for name_block in extended_match[last_name]:
                # if the name block has half of the match, add the other half
                if first_name_1 in name_block:
                    name_block.add(first_name_2)
                    found = True
                    break
                elif first_name_2 in name_block:
                    name_block.add(first_name_1)
                    found = True
                    break
            # If neither name is in the current set, create a new set, and place both names in it
            if not found:
                extended_match[last_name].append(set([first_name_1, first_name_2]))

            # extended_match_fix = extended_match.copy()
            #
            # for key, value in extended_match.items():
            #     for person in value:
            #         initial_list = []
            #         for name in person:
            #             #search for 1-2 letter middle initial as its own string
            #             letter_split_set = set()
            #             if re.search(r'\b([a-zA-Z][a-zA-Z]?)\b', name):
            #                 initial_list.append([re.search(r'\b([a-zA-Z][a-zA-Z]?)\b', name).group(1), name])
            #         initial_list.sort(key=lambda x: x[0])
            #         #find all first letters in the set
            #         first_letter_set = set(x[0][0] for x in initial_list)
            #         #check for trivial solution, where there is only 1 letter, and only one double letter solution, do nothing
            #         if len(first_letter_set) < 2 and len(set([x[0] for x in initial_list if len(x[0]) > 1])) < 2:
            #             break
            #         #need to add some complicated logic here, but for now we just removing these people
            #         else:
            #             print('Removing:', person, first_letter_set, initial_list, key, value)
            #             extended_match_fix[key].remove(person)

    return extended_match


def create_update_query_last_name():

    #Open the master table
    with open("output.csv", "r") as f:
        reader = csv.reader(f)
        csvlist = list(reader)


    #Using the Table, We want to create "people", where there are multiple matches...
    changes = personify_match_list(csvlist)

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
