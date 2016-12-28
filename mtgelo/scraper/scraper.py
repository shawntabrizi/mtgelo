import urllib
from bs4 import BeautifulSoup
import re
import daterangeparser
import html

from mtgelo.scraper.database import *

#global variable for db table size
dblength = 19


def customFixData(resultsrow, coverageid, eventid, roundid, rowid):
    #single pattern match
    patterns = []
    #multi-pattern match
    multipatterns = []
    # Fix messed up letters in names
    patterns.append([6, 1, '�sterberg', 'Österberg'])
    patterns.append([6, 1, 'Franz�n', 'Franzén'])
    patterns.append([6, 1, 'L�hrs', 'Lührs'])
    patterns.append([6, 1, 'J�bstl', 'Jöbstl'])
    patterns.append([6, 1, 'Andr�', 'Andre'])
    patterns.append([6, 1, 'St�phane', 'Stéphane'])
    patterns.append([6, 1, 'H�berli', 'Häberli'])
    multipatterns.append([6, 1, 'J�rg', 'Jürg'])
    patterns.append([6, 1, 'Koskim�ki', 'Koskimäki'])
    patterns.append([6, 1, '\?krbec', 'Skrbec'])
    multipatterns.append([6, 1, '\?iga', 'Ziga'])
    patterns.append([6, 1, 'Thor\?n', 'Thorén'])
    patterns.append([6, 1, 'Thor�n', 'Thorén'])
    patterns.append([6, 1, 'K�hn', 'Kühn'])
    patterns.append([6, 1, 'Kr�ger', 'Kröger'])
    multipatterns.append([6, 1, 'S�veges', 'Süveges'])
    patterns.append([6, 1, 'Bj�rn', 'Bjørn'])
    patterns.append([6, 1, 'J�rn', 'Jörn'])

    #patterns for cov 7, event 4
    patterns.append([7, 4, '\(M[E]?[X]?$', '(MEX)'])
    patterns.append([7, 4, '\(C[H]?[I]?$', '(CHI)'])
    patterns.append([7, 4, '\(A[R]?[G]?$', '(ARG)'])
    #patterns for cov 7, event 6
    patterns.append([7, 6, '\(T[H]?$', '(TH)'])
    patterns.append([7, 6, '\(M[Y]?$', '(MY)'])
    patterns.append([7, 6, '\(S[G]?$', '(SG)'])
    #patterns for cov 7, event 14
    patterns.append([7, 14, '\(E[S]?[P]?$', '(ESP)'])
    patterns.append([7, 14, '\(N[E]?[D]?$', '(NED)'])
    patterns.append([7, 14, '\(S[N]?[G]?$', '(SNG)'])
    patterns.append([7, 14, '\(G[E]?[R]?$', '(GER)'])
    patterns.append([7, 14, '\(M[E]?[X]?$', '(MEX)'])
    #patterns for cov 7, event 40
    patterns.append([7, 40, '\(1[7]?[0]?[0]?$', '(1700)'])
    # patterns for cov 7, event 33
    patterns.append([7, 33, '\[[\!]$', '[!]'])
    # patterns for cov 7, event 34
    patterns.append([7, 34, '\[[\!]?$', '[!]'])
    patterns.append([7, 34, '\[[\!]?\s\-', '[!] -'])
    # patterns for 8, 29
    patterns.append([8, 29, '\s[\d]*\,', ','])
    patterns.append([8, 29, '\(1', ''])
    # patterns for 9, 17
    patterns.append([9, 17, '\?sterberg', 'Österberg'])
    #patterns for cov 10, event 24
    patterns.append([10, 24, 'J\?g', 'Jörg'])
    patterns.append([10, 24, 'Fr\?\?ic', 'Frédéric'])
    patterns.append([10, 24, 'Jo\?', 'Joào'])
    patterns.append([10, 24, 'G\?ther', 'Günther'])
    #patterns for cov 10, event 26
    patterns.append([10, 26, '(\(Aich)\s\[', '(Aichi) ['])
    patterns.append([10, 26, 'Hasegawa\]', 'Hasegawa'])
    #patterns for cov 10, event 34
    patterns.append([10, 34, '\(Fukushima$', '(Fukushima)'])
    #patterns for cov 12, event 20
    patterns.append([12, 20, '\(Okayama\s\[', '(Okayama) ['])
    patterns.append([12, 20, '\(Hyo\s\[', '(Hyogo) ['])
    patterns.append([12, 20, '\(Osa\s\[', '(Osaka) ['])
    # patterns for cov 13, event 24
    patterns.append([13, 24, 'Jog', 'Jörg'])
    # patterns for cov 16, event 30
    patterns.append([15, 19, '\[TK\}', '[TK]'])
    #patterns for cov 16, event 30
    patterns.append([16, 30, '\(Yamagata$', '(Yamagata)'])
    patterns.append([16, 30, '\(Saitama', '(Saitama)'])
    patterns.append([16, 30, '\(Oosaka$', '(Osaka)'])
    patterns.append([16, 30, '\(Chiba$', '(Chiba)'])
    patterns.append([16, 30, '\(Aichi$', '(Aichi)'])
    patterns.append([16, 30, '\(Tokyo$', '(Tokyo)'])
    patterns.append([16, 30, '\(Hyogo$', '(Hyogo)'])
    patterns.append([16, 30, '\(Gunma$', '(Gunma)'])
    patterns.append([16, 30, '\(Hokkaido$', '(Hokkaido)'])
    patterns.append([16, 30, '\(Aomori$', '(Aomori)'])
    patterns.append([16, 30, '\(Nagano$', '(Nagano)'])
    patterns.append([16, 30, '\(Kanagawa$', '(Kanagawa)'])
    # 19 6
    patterns.append([19, 6, 'Jo\?o', 'Joao'])
    # patterns for cov 19, event 12
    patterns.append([19, 12, '\(tokyo\s\[', '(Tokyo) ['])
    patterns.append([19, 12, '\(sait\s\[', '(Saitama) ['])
    patterns.append([19, 12, '\(chib\s\[', '(Chiba) ['])
    # patterns for cov 19, event 23
    patterns.append([19, 23, '\(Hiroshima$', '(Hiroshima)'])
    # patterns for cov 19, event 42
    patterns.append([19, 42, '\(Kanagawa$', '(Kanagawa)'])
    #20 34
    patterns.append([20, 34, 'Jo\?o', 'Joao'])
    # 20 62 not 100% about this one... but it matches by last name.
    patterns.append([20, 62, 'Joerg', 'Jörg'])
    #21, 28
    patterns.append([21, 28, '\(kokubunji-ci', '(kokubunji-city)'])
    # patterns for cov 22, event 50
    multipatterns.append([22, 50, '^aaa\sVIP', 'VIP'])
    patterns.append([22, 50, '\[V\s', '[V] '])
    patterns.append([22, 50, '\[\s', '[V] '])

    #Commenting this out, just going to remove numbers from ALL names... may mess up some things
    #May need to revisit
    # # patterns for numbers at the end of some names
    # patterns.append([21, 57, '[0-9]*', ''])
    # patterns.append([22, 30, '[0-9]*', ''])
    # patterns.append([22, 31, '[0-9]*', ''])
    # patterns.append([22, 33, '[0-9]*', ''])
    # patterns.append([22, 37, '[0-9]*', ''])
    # patterns.append([22, 40, '[0-9]*', ''])
    # patterns.append([22, 45, '[0-9]*', ''])
    # patterns.append([22, 47, '[0-9]*', ''])
    # patterns.append([23, 12, '[0-9]*', ''])
    # patterns.append([23, 14, '[0-9]*', ''])
    # patterns.append([23, 16, '[0-9]*', ''])
    # patterns.append([23, 17, '[0-9]*', ''])

    #Only want to match a single pattern, so we break
    #player
    for pat in patterns:
        if coverageid == pat[0] and eventid == pat[1]:
            if re.search(pat[2], resultsrow[9]):
                resultsrow[9] = re.sub(pat[2], pat[3], resultsrow[9])
                break
    #opponent
    for pat in patterns:
        if coverageid == pat[0] and eventid == pat[1]:
            if re.search(pat[2], resultsrow[13]):
                resultsrow[13] = re.sub(pat[2], pat[3], resultsrow[13])
                break
    #For multi-pattern, so no break
    #player
    for pat in multipatterns:
        if coverageid == pat[0] and eventid == pat[1]:
            if re.search(pat[2], resultsrow[9]):
                resultsrow[9] = re.sub(pat[2], pat[3], resultsrow[9])
    #opponent
    for pat in multipatterns:
        if coverageid == pat[0] and eventid == pat[1]:
            if re.search(pat[2], resultsrow[13]):
                resultsrow[13] = re.sub(pat[2], pat[3], resultsrow[13])

    #fix some data that is doubly html encoded
    htmldecodelist = []
    htmldecodelist.append([16, 21])
    htmldecodelist.append([17, 24])
    htmldecodelist.append([18, 8])
    htmldecodelist.append([18, 9])
    htmldecodelist.append([18, 13])
    htmldecodelist.append([19, 22])

    #decode HTML strings
    for htmldecode in htmldecodelist:
        if coverageid == htmldecode[0] and eventid == htmldecode[1]:
            #not once... but twice... WHYYY
            resultsrow[9] = html.unescape(html.unescape(resultsrow[9]))
            resultsrow[13] = html.unescape(html.unescape(resultsrow[13]))

def processTeamName(resultsrow):
    garbagepat = []
    #remove '*Amateur*' from team name, and substrings of it...
    garbagepat.append('\*Ama[t]?[e]?[u]?[r]?[\*]?')
    #remove rank from team name '(123)'
    garbagepat.append('\(\d*\)')

    #here we want to remove all garbage patterns, so there is no break in the loop
    for pat in garbagepat:
        if re.search(pat, resultsrow[9]):
            resultsrow[9] = re.sub(pat, '', resultsrow[9])
        if re.search(pat, resultsrow[13]):
            resultsrow[13] = re.sub(pat, '', resultsrow[13])

def processName(resultsrow):
    garbagepat = []
    #remove '[!]' from the name... what is it even there for?
    garbagepat.append('\[\!\]')
    #remove * too
    garbagepat.append('\*')
    #remove '(DROPPED)'
    garbagepat.append('\(DROPPED\)')
    #remove rank from player name '(123)'
    garbagepat.append('\(\d*\)')
    #remove TM from player name... really?
    garbagepat.append(u'(\u2122)')
    #remove '(Amateur)'
    garbagepat.append('\(Amate[u]?[r]?[\)]?')
    #remove (VIP)
    garbagepat.append('\(VIP\)')
    #remove (P)
    garbagepat.append('\(P\)')
    # remove (See SK)
    garbagepat.append('\(See SK\)')
    #remove '(' at end of string
    garbagepat.append('\($')
    #remove '[???]'
    garbagepat.append('\[\?\?\?\]')
    #remove '[]'
    garbagepat.append('\[\]')
    #remove [ at the end of string
    garbagepat.append('\[$')
    #remove "VIP -"
    garbagepat.append('VIP -')
    #remove "VIP_"
    garbagepat.append('VIP_')
    # remove "aaVIP"
    garbagepat.append('aaVIP')
    #remove "ZVIP", "ZZVIP"... "Zzvip
    garbagepat.append('[zZ][zZ]?[zZ]?[vV][iI][pP]')
    #Remove "VIP"
    garbagepat.append('VIP')
    #remove "vip "
    garbagepat.append('vip ')
    #remove '-[v]'
    garbagepat.append('-\[[vV]\]')
    #remove '[V]', which also represents VIP
    garbagepat.append('\[[vV]\]')
    #remove '- [numbers]'
    garbagepat.append('\-\s[0-9]*')
    #remove '-' at the end
    garbagepat.append('\-$')
    # remove "ZZZVIP"
    garbagepat.append('ZZZVIP')
    #remove "zzVIP"
    garbagepat.append('zzVIP')
    #remove "aaa-"
    garbagepat.append('aaa-')
    #remove "AAA "
    garbagepat.append('AAA\s')
    #remove "ZZ "
    garbagepat.append('ZZ\s')
    # remove "Zzz_"
    garbagepat.append('[zZ][zZ][zZ]_')
    #remove "ZZSIS" and 'zzSIS'
    garbagepat.append('[zZ][zZ]SIS')
    #Remove "ZZZSB"
    garbagepat.append('ZZZSB')
    #remove "[zZ][zZ]3-"
    garbagepat.append('[zZ][zZ]3-')
    # remove "zzz"... "ZZZ"
    garbagepat.append('[zZ][zZ][zZ]')
    #remove numbers from names
    garbagepat.append('[0-9]*')



    #here we want to remove all garbage patterns, so there is no break in the loop
    for pat in garbagepat:
        if re.search(pat, resultsrow[9]):
            resultsrow[9] = re.sub(pat,'',resultsrow[9])
        if re.search(pat, resultsrow[13]):
            resultsrow[13] = re.sub(pat,'',resultsrow[13])

    #extract country from name
    #Order of these filters matter
    countrypat = []
    #extract country when it is '[ABC]'
    countrypat.append('(\[[a-zA-Z][a-zA-Z][a-zA-Z]?\])')
    #extract country when it is '(ABC)'
    countrypat.append('\(([a-zA-Z][a-zA-Z][a-zA-Z]?)\)')
    #extract country when it is '/ABC'
    countrypat.append('\/([A-Z][A-Z][A-Z]?)')
    #extract country when it is '- ABC'
    countrypat.append('\-\s?([A-Z][A-Z][A-Z]?)')
    #Then start to look for specific strings we know exist, mostly japanese countries
    countrypat.append('\(([aA]ichi)\)')
    countrypat.append('\(([aA]kita)\)')
    countrypat.append('\(([aA]omori)\)')
    countrypat.append('\(([cC]hamp)\)')
    countrypat.append('\(([cC]hiba)\)')
    countrypat.append('\(([eE]hime)\)')
    countrypat.append('\(([fF]ukushima)\)')
    countrypat.append('\(([fF]ukui)\)')
    countrypat.append('\(([fF]ukuoka)\)')
    countrypat.append('\(([fF]uchu)\)')
    countrypat.append('\(([gG]ifu)\)')
    countrypat.append('\(([gG]unma)\)')
    countrypat.append('\(([hH]yogo)\)')
    countrypat.append('\(([hH]yougo)\)')
    countrypat.append('\(([hH]okkaido)\)')
    countrypat.append('\(([hH]iroshima)\)')
    countrypat.append('\(([hH]ino)\)')
    countrypat.append('\(([iI]shikawa)\)')
    countrypat.append('\(([iI]wate)\)')
    countrypat.append('\(([iI]baraki)\)')
    countrypat.append('\(([jJ]apan)\)')
    countrypat.append('\(([kK]umamoto)[\)]?')
    countrypat.append('\(([kK]agoshima)\)')
    countrypat.append('\(([kK]awasaki)\)')
    countrypat.append('\(([kK]yoto)\)')
    countrypat.append('\(([kK]anagawa)\)')
    countrypat.append('\(([kK]okubunji-[cC]ity)\)')
    countrypat.append('\(([mM]iyagi)\)')
    countrypat.append('\(([mM]ie)\)')
    countrypat.append('\(([mM]achida)\)')
    countrypat.append('\(([nN]agano)\)')
    countrypat.append('\(([nN]iigata)\)')
    countrypat.append('\(([nN]ara)\)')
    countrypat.append('\(([oO]kayama)\)')
    countrypat.append('\(([oO]saka)\)')
    countrypat.append('\(([oO]saka\-[cC]ity)\)')
    countrypat.append('\(([sS]endai)\)')
    countrypat.append('\(([sS]higa)\)')
    countrypat.append('\(([sS]aitama)\)')
    countrypat.append('\(([sS]apporo)\)')
    countrypat.append('\(([sS]hizuoka)\)')
    countrypat.append('\(([sS]etagaya\-[kK]u)\)')
    countrypat.append('\(([tT]okyo)\)')
    countrypat.append('\(([tT]ochigi)\)')
    countrypat.append('\(([tT]ottori)\)')
    countrypat.append('\(([tT]oyama)\)')
    countrypat.append('\(([tT]okushim[a]?)[\)]?')
    countrypat.append('\(([yY]amagata)[\)]?')
    #Also some United States Regions
    countrypat.append('\[(SOCAL)\]?')
    countrypat.append('\[(MATL)\]?')
    countrypat.append('\[(NOCAL)\]?')
    countrypat.append('\[(NENG)\]?')

    #These are not countries, but most likely names, that can be used for uniqueness


    #here we only want to remove one such country pattern, but we do not break...
    #But some have multiple country patterns, so we append other country patters in addition to the patterms we found
    #probably need to fix this up to make it more approachable
    #player
    for pat in countrypat:
        if re.search(pat, resultsrow[9]):
            if resultsrow[11] != '':
                resultsrow[11] += ';'
            resultsrow[11] += re.search(pat, resultsrow[9]).group(1).upper()
            resultsrow[9] = re.sub(pat, '', resultsrow[9])

    #opponent
    for pat in countrypat:
        if re.search(pat, resultsrow[13]):
            if resultsrow[15] != '':
                resultsrow[15] += ';'
            resultsrow[15] += re.search(pat, resultsrow[13]).group(1).upper()
            resultsrow[13] = re.sub(pat, '', resultsrow[13])


    #get first name and last name
    namepat = []
    #comma seperated
    namepat.append('(.*)\,(.*)')
    #space seperated, find the first space...
    namepat.append('([^\s]+)\s(.*)')
    #again, we only want to apply one of these rules once, so once we find a match, break
    #order matters here, so we want to search for comma first
    #player
    for pat in namepat:
        if re.search(pat, resultsrow[9]):
            resultsrow[10] = re.search(pat, resultsrow[9]).group(1)
            resultsrow[9] = re.search(pat, resultsrow[9]).group(2)
            break
    #opponent
    for pat in namepat:
        if re.search(pat, resultsrow[13]):
            resultsrow[14] = re.search(pat, resultsrow[13]).group(1)
            resultsrow[13] = re.search(pat, resultsrow[13]).group(2)
            break

    #Look specifically for the cases where an Bye is awarded for having plainswalker points, and then flip the order of them, and regular their case
    if re.match('bye', resultsrow[13], re.I) and re.match('awarded', resultsrow[14], re.I):
        resultsrow[13] = 'Awarded'
        resultsrow[14] = u'BYE'

def processResult(resultsrow):
    #take "won 2-0" and turn it into 'won' and '2-0'... etc
    winpat = '(won)|(win)'
    drawpat = '(drew)|(draw)'
    lostpat = '(lost)|(loss)'

    resultvalue = None
    score = []

    #win pattern
    if re.search(winpat, resultsrow[12], re.I):
        resultvalue = 'Won'
        resultsrow[12] = re.sub(winpat, '', resultsrow[12], 0, re.I)
    #draw pattern
    elif re.search(drawpat, resultsrow[12], re.I):
        resultvalue = 'Drew'
        resultsrow[12] = re.sub(drawpat, '', resultsrow[12], 0, re.I)
    #lost pattern
    elif re.search(lostpat, resultsrow[12], re.I):
        resultvalue = 'Lost'
        resultsrow[12] = re.sub(lostpat, '', resultsrow[12], 0, re.I)

    #fix up the numbers if the results are double digits
    numberpat = []
    numberpat.append(['02\-', '2-'])
    numberpat.append(['01\-', '1-'])
    numberpat.append(['00\-', '0-'])
    numberpat.append(['\-02', '-2'])
    numberpat.append(['\-01', '-1'])
    numberpat.append(['\-00', '-0'])
    numberpat.append(['02\/', '2/'])
    numberpat.append(['01\/', '1/'])
    numberpat.append(['00\/', '0/'])
    numberpat.append(['\/02', '/2'])
    numberpat.append(['\/01', '/1'])
    numberpat.append(['\/00', '/0'])
    for pat in numberpat:
        if re.search(pat[0], resultsrow[12]):
            resultsrow[12] = re.sub(pat[0], pat[1], resultsrow[12])

    scorepat = '(\d)'
    if re.search(scorepat, resultsrow[12]):
        score = re.findall(scorepat, resultsrow[12])
        for s in score:
            try:
                s = int(s)
            except:
                print("Could not convert score to int: ", s)

    if len(score) == 2:
       resultsrow[16] = score[0]
       resultsrow[17] = score[1]
       resultsrow[18] = 0
    elif len(score) == 3:
       resultsrow[16] = score[0]
       resultsrow[17] = score[1]
       resultsrow[18] = score[2]

    #if resultvalue is empty still, but score as a value, try to determine result off of score
    if resultvalue == None:
        #here I am ignoring the 3rd score value which represents "draws"... is that bad?
        if len(score) == 2 or len(score) == 3:
            if score[0] < score[1]:
                resultvalue = 'Lost'
            elif score[0] > score[1]:
                resultvalue = 'Won'
            elif score[0] == score[1]:
                resultvalue = 'Drew'
    #put won, lost, or draw into the resultrow
    if resultvalue != None:
        resultsrow[12] = resultvalue

    #check if result is a bye, then put it in the right spot
    if re.search('bye', resultsrow[12], re.I):
                        resultsrow[12] = ''
                        resultsrow[13] = ''
                        resultsrow[14] = 'BYE'

def customtable(coverageloop, eventloop, resultloop, tableindex, playerindex, playercountryindex, resultindex, opponentindex, opponentcountryindex):
    #try and fix custom tables that are hard to detect by header title
    customindexes = []
    customindexes.append([6, 15, 0, 1, None, 2, 3, None])
    customindexes.append([6, 16, None, 0, None, 1, 2, None])
    #JSS
    customindexes.append([5, 2, None, 0, None, 2, 1, None])
    #Latin America Champ
    customindexes.append([6, 5, None, 0, None, 2, 1, None])
    #Super Series
    customindexes.append([6, 7, None, 0, None, 2, 1, None])
    #US Nationals
    customindexes.append([6, 8, None, 0, None, 2, 1, None])
    #Nagoya, Japan 2002
    customindexes.append([8, 21, 0, 1, None, 2, 4, None])
    #GP Beijing 2015
    customindexes.append([22, 48, 0, 1, None, 2, 4, None])
    #GP Detriot 2015
    customindexes.append([22, 55, 0, 1, None, 2, 4, None])

    for customindex in customindexes:
        if coverageloop == customindex[0] and eventloop == customindex[1]:
            tableindex = customindex[2]
            playerindex = customindex[3]
            playercountryindex = customindex[4]
            resultindex = customindex[5]
            opponentindex = customindex[6]
            opponentcountryindex = customindex[7]
            break

    customindexesbyround = []
    #US Nationals round 6
    customindexesbyround.append([6, 8, 6, 0, 2, None, 3, 5, None])
    for customindex in customindexesbyround:
        if coverageloop == customindex[0] and eventloop == customindex[1] and resultloop == customindex[2]:
            tableindex = customindex[3]
            playerindex = customindex[4]
            playercountryindex = customindex[5]
            resultindex = customindex[6]
            opponentindex = customindex[7]
            opponentcountryindex = customindex[8]
            break

    return tableindex, playerindex, playercountryindex, resultindex, opponentindex, opponentcountryindex



def saveResults(coverageloop, eventloop, resultloop, startrow, endrow, resulturl, eventtype, eventname, date, round):
    #resulturl = "http://magic.wizards.com/en/articles/archive/event-coverage/grand-prix-guadalajara-round-14-results-2013-05-26"
    try:
        htmlFile = urllib.request.urlopen(resulturl)
        resulturl = htmlFile.geturl()
        pageok = True
    except:
        pageok = False


    if (re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", resulturl)):
        #checks for a better date, but ignores 2000-01-01, which is a bad date that wizards sticks in places
        tempdate = re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", resulturl).group(1)
        if tempdate != '2000-01-01':
            date = tempdate
    #some pages do not exist... #wizardProblems
    if (pageok):
        rawHTML = htmlFile.read()
        soup = BeautifulSoup(rawHTML, "lxml")
        #is there a table? Sortrow is a weird tag that they sometimes use for the header??
        #but sometimes sortrow is blank, and we need to ignore it
        #hypothesis: sortrow is only blank if it is not 'in the table'
        table = soup.find('table')
        if table:
            table = table.findAll(['tr','sortrow'])
        if table:
            #starting to parse the table
            totalresults = []
            #establish header row index
            headerrowindexes = table[0].findAll(['th','td'])
            tableindex = None
            playerindex = None
            playercountryindex = None
            resultindex = None
            opponentindex = None
            opponentcountryindex = None
            #track if player or team
            isplayer = None
            #default table size
            if len(headerrowindexes) == 7:
                for headerrowindex in headerrowindexes:
                    if re.search('player',headerrowindex.text, re.I):
                        isplayer = True
                    elif re.search('team',headerrowindex.text, re.I):
                        isplayer = False
                tableindex = 0
                playerindex = 1
                playercountryindex = 2
                resultindex = 3
                opponentindex = 5
                opponentcountryindex = 6
            else:
                print (headerrowindexes)
                for index,headerrowindex in enumerate(headerrowindexes):
                    if re.search('table', headerrowindex.text, re.I):
                        tableindex = index
                    elif re.search('player',headerrowindex.text, re.I):
                        playerindex = index
                        isplayer = True
                    elif re.search('team',headerrowindex.text, re.I):
                        playerindex = index
                        isplayer = False
                    elif re.search('result', headerrowindex.text, re.I):
                        resultindex = index
                    elif re.search('opponent', headerrowindex.text, re.I):
                        opponentindex = index

            #override the searched mapping with custom settings
            tableindex, playerindex, playercountryindex, resultindex, opponentindex, opponentcountryindex = customtable(coverageloop, eventloop, resultloop, tableindex, playerindex, playercountryindex, resultindex, opponentindex, opponentcountryindex)
            print(tableindex, playerindex, resultindex, opponentindex)

            tablelength = len(table)
            if endrow == 0:
                endrow = tablelength
            if startrow == 0:
                #skip first row, which is a header row
                startrow = 1
            loop = startrow
            while (loop < tablelength and loop < endrow):
                row = table[loop]
                #table is a fixed size
                resultsrow = [''] * dblength
                #initial data entry
                #be able to uniquely identify a loop
                resultsrow[0] = coverageloop
                resultsrow[1] = eventloop
                resultsrow[2] = resultloop
                resultsrow[3] = loop
                #standard metadata from the other loops
                resultsrow[4] = eventtype
                resultsrow[5] = eventname
                resultsrow[6] = date
                resultsrow[7] = round
                #reading each coloumn in a row
                tds = row.findAll('td')
                if len(tds) == len(headerrowindexes):
                    if tableindex != None and tableindex < len(tds):
                        resultsrow[8] = tds[tableindex].text
                    if playerindex != None and playerindex < len(tds):
                        resultsrow[9] = tds[playerindex].text
                    if playercountryindex != None and playercountryindex < len(tds):
                        resultsrow[11] = tds[playercountryindex].text
                    if resultindex != None and resultindex < len(tds):
                        resultsrow[12] = tds[resultindex].text
                    if opponentindex != None and opponentindex < len(tds):
                        resultsrow[13] = tds[opponentindex].text
                    if opponentcountryindex != None and opponentcountryindex < len(tds):
                        resultsrow[15] = tds[opponentcountryindex].text
                    #Fix Wizards Data!
                    customFixData(resultsrow, coverageloop, eventloop, resultloop, loop)
                    #process names to pull out country data
                    if isplayer:
                        processName(resultsrow)
                    else:
                        processTeamName(resultsrow)
                        resultsrow[10] = 'TEAM EVENT'
                        resultsrow[14] = 'TEAM EVENT'
                    #process country to only have letters and semicolon
                    resultsrow[11] = re.sub('[^a-zA-Z\;]','',resultsrow[11])
                    resultsrow[15] = re.sub('[^a-zA-Z\;]','',resultsrow[15])
                    #process the result value
                    processResult(resultsrow)
                    #remove beginning and ending whitespace
                    #also convert to INT if possible
                    striploop = 0
                    while (striploop < len(resultsrow)):
                        #check that it is not an int
                        if not isinstance(resultsrow[striploop], int):
                            try:
                                #either turn it into a number
                                resultsrow[striploop] = int(resultsrow[striploop])
                            except:
                                #or strip the string
                                resultsrow[striploop] = resultsrow[striploop].strip()
                        striploop = striploop + 1
                    #write to DB
                    playerHistoryToDB(resultsrow)
                loop = loop + 1
        else:
            errorresults = ['']*dblength
            errorresults[0] = coverageloop
            errorresults[1] = eventloop
            errorresults[2] = resultloop
            errorresults[3] = ''
            errorresults[4] = eventtype
            errorresults[5] = eventname
            errorresults[6] = date
            errorresults[7] = round
            playerHistoryToDB(errorresults)
    else:
        #if the page doesnt exist
        errorresults = ['']*dblength
        errorresults[0] = coverageloop
        errorresults[1] = eventloop
        errorresults[2] = resultloop
        errorresults[3] = ''
        errorresults[4] = eventtype
        errorresults[5] = eventname
        errorresults[6] = date
        errorresults[7] = round
        playerHistoryToDB(errorresults)

def getAllResults(coverageloop, eventloop, startround, endround, startrow, endrow, eventurl, eventtype, eventname, date):
    #eventurl = 'http://magic.wizards.com/en/events/coverage/gpveg15-1'
    if(eventurl.find("magic.wizards.com") == -1):
        eventurl = urllib.parse.urljoin('http://magic.wizards.com/en/events/coverage', eventurl)
    htmlFile = urllib.request.urlopen(eventurl)
    eventurl = htmlFile.geturl()
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML, "lxml")

    print (eventurl)
    round = ''
    results = [[]]
    resultsurls = []
    #event page has a section with "by-day" class
    bydays = soup.findAll('div', attrs={"class": "by-day"})
    if (len(bydays) == 0):
        #if it has no "by-day" then look for class "results"...
        bydays = soup.findAll('div', attrs={"class": "results"})
    if (len(bydays) != 0):
        for byday in bydays:
            if (byday.find('p', text=re.compile("results", re.I))):
                resultsurls = byday.findAll("a")
    elif soup.findAll('a', text=re.compile('(result)|(results)', re.I)):
        #if we never found a section where results were all organized, look for links with the word "results" on the page
        resultsurls = soup.findAll('a', text=re.compile('(result)|(results)', re.I))
        #only look at results specified

    resultslength = len(resultsurls)
    if 0 < resultslength:
        if endround == 0:
            endround = resultslength
        loop = startround
        while (loop < resultslength and loop < endround):
            #grab the loop we are on
            resulturl = resultsurls[loop]
            if(resulturl['href'].find("magic.wizards.com") == -1):
                resulturl['href'] = urllib.parse.urljoin(eventurl, resulturl['href'])
            print (resulturl['href'])
            if not (re.search('player', resulturl.text, re.I)):
                #Find Round Number
                #Sometimes Round Number is Right in the URL
                if (re.search('round-(\d+)',resulturl['href'])):
                    round = re.search('round-(\d+)',resulturl['href']).group(1)
                #Otherwise look at the link text for a number
                elif re.search('(\d+)',resulturl.text):
                    round = re.search('(\d+)', resulturl.text).group(1)
                #cry
                else:
                    round = ''
                if not (resulturl['href'] == None or eventname == None or round == None):
                    results = saveResults(coverageloop, eventloop, loop, startrow, endrow, resulturl['href'], eventtype, eventname, date, round)
            #iterate loop
            loop = loop + 1
    else:
        #if nothing useful on the page
        errorresults = ['']*dblength
        errorresults[0] = coverageloop
        errorresults[1] = eventloop
        errorresults[2] = ''
        errorresults[3] = ''
        errorresults[4] = eventtype
        errorresults[5] = eventname
        errorresults[6] = date
        print (errorresults)
        playerHistoryToDB(errorresults)


def findDate (eventelem):
    #default value
    datestring = ''
    if eventelem.nextSibling:
        if re.match('\s?\(([^)]+)\)?', str(eventelem.nextSibling)):
            #match parenthesis content at the begginning
            paren = re.match('\s?\(([^)]+)\)?', str(eventelem.nextSibling)).group(1)

            #match date substring
            if re.search('([a-zA-Z]+\.?\s?(\d).*(\d))',paren):
                date = re.search('([a-zA-Z]+\.?\s?(\d).*(\d))',paren).group(1)
                #get rid of bad dash
                date = re.sub(u"\u2013", "-", date)
                try:
                    if daterangeparser.parse(date):
                        datestring = str(daterangeparser.parse(date)[0].date())
                except:
                    print ("--Date Parse Exception--")
    return datestring


def getAllCoverageEvents(startcoverage=0,endcoverage=0,startevent=0,endevent=0,startround=0,endround=0,startrow=0,endrow=0):
    coverageURL = "http://magic.wizards.com/en/events/coverage"
    htmlFile = urllib.request.urlopen(coverageURL)
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML, "lxml")

    sections = soup.findAll('div', attrs={'class':'bean_block bean_block_html bean--wiz-content-html-block '})
    #Reverse the order, starting from oldest... so that we can be consistant about which loop is which year
    sections = list(reversed(sections))
    sectionslength = len(sections)
    if endcoverage == 0:
        endcoverage = sectionslength
    loop = startcoverage
    while (loop < sectionslength and loop < endcoverage):
        #grab the loop we are on
        section = sections[loop]

        season = section.find('h2')
        print (season)
        eventtype=""
        eventname=""
        eventurlslist = []
        eventnameslist = []
        eventdateslist = []
        eventtypeslist = []
        #different patterns to match per season, starting from the first season 1994
        #1994 Season to 2008 Season, 15 total sections
        if (loop < 15):
            eventcontainer = section.find('p')
            eventsoup = eventcontainer.findAll(['b','a'])
            for eventelem in eventsoup:
                if (eventelem.name == 'b'):
                    eventtype = eventelem.text
                if (eventelem.name == 'a'):
                    eventname = eventelem.text
                    eventurl = eventelem['href']
                    date = findDate(eventelem)
                    #print eventurl, eventtype, eventname
                    eventtypeslist.append(eventtype)
                    eventurlslist.append(eventurl)
                    eventnameslist.append(eventname)
                    eventdateslist.append(date)

        #2009 Season
        elif (loop == 15):
            eventtypes = section.findAll('p')
            for eventtypeelem in eventtypes:
                eventtype = eventtypeelem.find('b').text
                eventnames = eventtypeelem.findAll('a')
                for eventnamehtml in eventnames:
                    eventname = eventnamehtml.text
                    eventurl = eventnamehtml['href']
                    date = findDate(eventnamehtml)
                    #print eventurl, eventtype, eventname
                    eventtypeslist.append(eventtype)
                    eventurlslist.append(eventurl)
                    eventnameslist.append(eventname)
                    eventdateslist.append(date)
        #2010 Season
        elif (loop == 16):
            eventtypes = section.findAll('p')
            del eventtypes[1] #there is an empty p tag... whyyyyyy?
            for eventtypeelem in eventtypes:
                eventtype = eventtypeelem.find('b').text
                if (eventtype == 'hampionships'): # missing a C.... WHYYYYY?
                    eventtype = 'Championships'
                eventnames = eventtypeelem.findAll('a')
                for eventnamehtml in eventnames:
                    eventname = eventnamehtml.text
                    eventurl = eventnamehtml['href']
                    date = findDate(eventnamehtml)
                    #print eventurl, eventtype, eventname
                    eventtypeslist.append(eventtype)
                    eventurlslist.append(eventurl)
                    eventnameslist.append(eventname)
                    eventdateslist.append(date)
        #2011 Season to 2012 Season
        elif (17 <= loop < 19):
            eventtypes = section.findAll('p')
            for eventtypeelem in eventtypes:
                if (eventtypeelem.find('strong')):
                    eventtype = eventtypeelem.find('strong').text
                    eventnames = eventtypeelem.findAll('a')
                    for eventnamehtml in eventnames:
                        eventname = eventnamehtml.text
                        eventurl = eventnamehtml['href']
                        date = findDate(eventnamehtml)
                        #print eventurl, eventtype, eventname
                        eventtypeslist.append(eventtype)
                        eventurlslist.append(eventurl)
                        eventnameslist.append(eventname)
                        eventdateslist.append(date)
        #2012-13 Season
        elif (loop == 19):
            eventcontainer = section.find('p')
            eventsoup = eventcontainer.findAll(['strong','a'])
            for eventelem in eventsoup:
                if (eventelem.name == 'strong'):
                    if(re.search('[a-zA-Z]', eventelem.text)):
                        eventtype = eventelem.text
                if (eventelem.name == 'a'):
                    eventname = eventelem.text
                    eventurl = eventelem['href']
                    date = findDate(eventelem)
                    #print eventurl, eventtype, eventname
                    eventtypeslist.append(eventtype)
                    eventurlslist.append(eventurl)
                    eventnameslist.append(eventname)
                    eventdateslist.append(date)
        #2013-2014 Season to 2014-2015
        elif(20 <= loop < 22):
            eventsoup = section.findAll(['strong','a'])
            for eventelem in eventsoup:
                if (eventelem.name == 'strong'):
                    if(re.search('[a-zA-Z]', eventelem.text)):
                        eventtype = eventelem.text
                if (eventelem.name == 'a'):
                    eventname = eventelem.text
                    eventurl = eventelem['href']
                    date = findDate(eventelem)
                    #print eventurl, eventtype, eventname
                    eventtypeslist.append(eventtype)
                    eventurlslist.append(eventurl)
                    eventnameslist.append(eventname)
                    eventdateslist.append(date)
        #2015-2016 Season to present
        elif(22 <= loop):
            eventsoup = section.findAll(['h4','a'])
            for eventelem in eventsoup:
                if (eventelem.name == 'h4'):
                    if(re.search('[a-zA-Z]', eventelem.text)):
                        eventtype = eventelem.text
                if (eventelem.name == 'a'):
                    eventname = eventelem.text
                    eventurl = eventelem['href']
                    date = findDate(eventelem)
                    #print eventurl, eventtype, eventname
                    eventtypeslist.append(eventtype)
                    eventurlslist.append(eventurl)
                    eventnameslist.append(eventname)
                    eventdateslist.append(date)
        eventurlslength = len(eventurlslist)
        if endevent == 0:
            endeventloop = eventurlslength
        else:
            endeventloop = endevent
        eventloop = startevent
        while (eventloop < eventurlslength and eventloop < endeventloop):
            eventurl = eventurlslist[eventloop]
            eventtype = eventtypeslist[eventloop]
            eventname = eventnameslist[eventloop]
            date = eventdateslist[eventloop]
            getAllResults(loop, eventloop, startround,endround, startrow, endrow, eventurl, eventtype, eventname, date)
            eventloop = eventloop + 1

        #iterate the loop
        loop = loop + 1