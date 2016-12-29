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
