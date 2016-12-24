import urllib
from bs4 import BeautifulSoup
import re
import urlparse
import daterangeparser

from database import *

#global variable for db table size
dblength = 16

def processName(resultsrow):
    garbagepat = []
    #remove '[!]' from the name... what is it even there for?
    garbagepat.append('\[\!\]')
    #remove * too
    garbagepat.append('\*')
    #remove rank from player name '(123)'
    garbagepat.append('\(\d*\)')
    
    for pat in garbagepat:
        if re.search(pat, resultsrow[9]):
            resultsrow[9] = re.sub(pat,'',resultsrow[9])
        if re.search(pat, resultsrow[13]):
            resultsrow[13] = re.sub(pat,'',resultsrow[13])
    #extract country from name
    countrypat = []
    #extract country when it is '[ABC]'
    countrypat.append('(\[[A-Z][A-Z][A-Z]?\])')
    #extract country when it is '/ABC'
    countrypat.append('\/([A-Z][A-Z][A-Z]?)')
    #extract country when it is '- ABC'
    countrypat.append('\-\s?([A-Z][A-Z][A-Z]?)')
    #extract country when it is '(ABC)'
    countrypat.append('\(([A-Z][A-Z][A-Z]?)\)')
    #player
    for pat in countrypat:
        if re.search(pat, resultsrow[9]):
            resultsrow[11] = re.search(pat, resultsrow[9]).group(1)
            resultsrow[9] = re.sub(pat, '', resultsrow[9])
            break
    #opponent
    for pat in countrypat:
        if re.search(pat, resultsrow[13]):
            resultsrow[15] = re.search(pat, resultsrow[13]).group(1)
            resultsrow[13] = re.sub(pat, '', resultsrow[13])
            break

    #get first name and last name
    namepat = []
    #comma seperated
    namepat.append('(.*)\,(.*)')
    #space seperated, find the first space...
    namepat.append('([^\s]+)\s(.*)')
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
    if re.match('bye', resultsrow[13], re.I) and re.match('awarded', resultsrow[14], re.I):
        resultsrow[13] = 'Awarded'
        resultsrow[14] = u'BYE'

def saveResults(coverageloop, eventloop, resultloop, startrow, endrow, resulturl, eventtype, eventname, date, round):
    #resulturl = "http://magic.wizards.com/en/articles/archive/event-coverage/grand-prix-guadalajara-round-14-results-2013-05-26"
    htmlFile = urllib.urlopen(resulturl)
    resulturl = htmlFile.geturl()

    if (re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", resulturl)):
        #checks for a better date, but ignores 2000-01-01, which is a bad date that wizards sticks in places
        tempdate = re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", resulturl).group(1)
        if tempdate != '2000-01-01':
            date = tempdate
    #some pages do not exist... #wizardProblems
    if (htmlFile.getcode() == 200):
        rawHTML = htmlFile.read()
        soup = BeautifulSoup(rawHTML)
        #is there a table? Sortrow is a weird tag that they sometimes use for the header??
        #but sometimes sortrow is blank, and we need to ignore it
        #hypothesis: sortrow is only blank if it is not 'in the table'
        table = soup.find('table')
        if table:
            table = table.findAll(['tr','sortrow'])
        if table:
            print table
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
                print headerrowindexes
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
            print (tableindex, playerindex, resultindex, opponentindex)
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
                if len(tds) == len (headerrowindexes):
                    if tableindex != None:
                        resultsrow[8] = tds[tableindex].text
                    if playerindex != None:
                        resultsrow[9] = tds[playerindex].text
                    if playercountryindex != None:
                        resultsrow[11] = tds[playercountryindex].text
                    if resultindex != None:
                        resultsrow[12] = tds[resultindex].text
                    if opponentindex != None:
                        resultsrow[13] = tds[opponentindex].text
                    if opponentcountryindex != None:
                        resultsrow[15] = tds[opponentcountryindex].text
                    #process names to pull out country data
                    if isplayer:
                        processName(resultsrow)
                    else:
                        resultsrow[10] = 'TEAM EVENT'
                        resultsrow[14] = 'TEAM EVENT'
                    #process country to only have letters
                    resultsrow[11] = re.sub('[^a-zA-Z]','',resultsrow[11])
                    resultsrow[15] = re.sub('[^a-zA-Z]','',resultsrow[15])
                    #check if result is BYE, and put it in the Opponent Last Name, clear first name
                    if re.search('bye', resultsrow[8], re.I):
                        resultsrow[12] = ''
                        resultsrow[13] = ''
                        resultsrow[14] = 'BYE'
                    #remove beginning and ending whitespace
                    #also convert to INT if possible
                    striploop = 0
                    while (striploop < len(resultsrow)):
                        #check that it is not an int
                        if not isinstance(resultsrow[striploop], int):
                            try:
                                resultsrow[striploop] = int(resultsrow[striploop])
                            except:
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
        eventurl = urlparse.urljoin('http://magic.wizards.com/en/events/coverage', eventurl)
    htmlFile = urllib.urlopen(eventurl)
    eventurl = htmlFile.geturl()
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML)

    print eventurl
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
                resulturl['href'] = urlparse.urljoin(eventurl, resulturl['href'])
            print resulturl['href']
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
        print errorresults
        playerHistoryToDB(errorresults)


def findDate (eventelem):
    #default value
    datestring = ''
    if eventelem.nextSibling:
        if re.match('\s?\(([^)]+)\)?', unicode(eventelem.nextSibling)):
            #match parenthesis content at the begginning
            paren = re.match('\s?\(([^)]+)\)?', unicode(eventelem.nextSibling)).group(1)
            
            #match date substring
            if re.search('([a-zA-Z]+\.?\s?(\d).*(\d))',paren):
                date = re.search('([a-zA-Z]+\.?\s?(\d).*(\d))',paren).group(1)
                #get rid of bad dash
                date = re.sub(u"\u2013", "-", date)
                try:
                    if daterangeparser.parse(date):
                        datestring = unicode(daterangeparser.parse(date)[0].date())
                except:
                    print "--Date Parse Exception--"
    return datestring

def getAllCoverageEvents(startcoverage=0,endcoverage=0,startevent=0,endevent=0,startround=0,endround=0,startrow=0,endrow=0):
    coverageURL = "http://magic.wizards.com/en/events/coverage"
    htmlFile = urllib.urlopen(coverageURL)
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML)
    
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
        print season
        eventtype=""
        eventname=""
        eventurls = []
        eventnames = []
        eventdates = []
        eventtypes = []
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
                    eventtypes.append(eventtype)
                    eventurls.append(eventurl)
                    eventnames.append(eventname)
                    eventdates.append(date)
                    
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
                    eventtypes.append(eventtype)
                    eventurls.append(eventurl)
                    eventnames.append(eventname)
                    eventdates.append(date)
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
                    eventtypes.append(eventtype)
                    eventurls.append(eventurl)
                    eventnames.append(eventname)
                    eventdates.append(date)
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
                        eventtypes.append(eventtype)
                        eventurls.append(eventurl)
                        eventnames.append(eventname)
                        eventdates.append(date)
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
                    eventtypes.append(eventtype)
                    eventurls.append(eventurl)
                    eventnames.append(eventname)
                    eventdates.append(date)
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
                    eventtypes.append(eventtype)
                    eventurls.append(eventurl)
                    eventnames.append(eventname)
                    eventdates.append(date)
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
                    eventtypes.append(eventtype)
                    eventurls.append(eventurl)
                    eventnames.append(eventname)
                    eventdates.append(date)
        eventurlslength = len(eventurls)
        if endevent == 0:
            endevent = eventurlslength
        eventloop = startevent
        while (eventloop < eventurlslength and eventloop < endevent):
            eventurl = eventurls[eventloop]
            eventtype = eventtypes[eventloop]
            eventname = eventnames[eventloop]
            date = eventdates[eventloop]
            getAllResults(loop, eventloop, startround,endround, startrow, endrow, eventurl, eventtype, eventname, date)
            eventloop = eventloop + 1

        #iterate the loop
        loop = loop + 1