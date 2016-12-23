import urllib
from bs4 import BeautifulSoup
import re
import urlparse
import daterangeparser

from database import *

def processName(resultsrow):
    garbagepat = []
    #remove '[!]' from the name... what is it even there for?
    garbagepat.append('\[\!\]')
    #remove * too
    garbagepat.append('\*')
    #remove rank from player name '(123)'
    garbagepat.append('\(\d*\)')
    
    for pat in garbagepat:
        if re.search(pat, resultsrow[5]):
            resultsrow[5] = re.sub(pat,'',resultsrow[5])
        if re.search(pat, resultsrow[9]):
            resultsrow[9] = re.sub(pat,'',resultsrow[9])


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
        if re.search(pat, resultsrow[5]):
            resultsrow[7] = re.search(pat, resultsrow[5]).group(1)
            resultsrow[5] = re.sub(pat, '', resultsrow[5])
            break
    #opponent
    for pat in countrypat:
        if re.search(pat, resultsrow[9]):
            resultsrow[11] = re.search(pat, resultsrow[9]).group(1)
            resultsrow[9] = re.sub(pat, '', resultsrow[9])
            break

    #get first name and last name
    namepat = []
    #comma seperated
    namepat.append('(.*)\,(.*)')
    #space seperated, find the first space...
    namepat.append('([^\s]+)\s(.*)')
    #player
    for pat in namepat:
        if re.search(pat, resultsrow[5]):
            resultsrow[6] = re.search(pat, resultsrow[5]).group(1)
            resultsrow[5] = re.search(pat, resultsrow[5]).group(2)
            break
    #opponent
    for pat in namepat:
        if re.search(pat, resultsrow[9]):
            resultsrow[10] = re.search(pat, resultsrow[9]).group(1)
            resultsrow[9] = re.search(pat, resultsrow[9]).group(2)
            break
    if re.match('bye', resultsrow[9], re.I) and re.match('awarded', resultsrow[10], re.I):
        resultsrow[9] = 'Awarded'
        resultsrow[10] = u'BYE'

def saveResults(loop, resulturl, eventtype, eventname, date, round):
    #resulturl = "http://magic.wizards.com/en/events/coverage/gplil16/round-12-results-2016-08-28"
    htmlFile = urllib.urlopen(resulturl)
    resulturl = htmlFile.geturl()

    if (re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", resulturl)):
        #checks for a better date, but ignores 2000-01-01, which is a bad date that wizards sticks in places
        tempdate = re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", resulturl).group(1)
        if tempdate != '2000-01-01':
            date = tempdate
    #some pages do not exist... #wizardProblems
    if (htmlFile.getcode() == 200):
        print 'opened'
        rawHTML = htmlFile.read()
        soup = BeautifulSoup(rawHTML)
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
            for row in table[1:]: #skip first row, which is a header row
                #table is a fixed size, 12
                resultsrow = [''] * 12
                #initial data entry
                resultsrow[0] = eventtype
                resultsrow[1] = eventname
                resultsrow[2] = date
                resultsrow[3] = round
                #reading each coloumn in a row
                tds = row.findAll('td')
                if len(tds) == len (headerrowindexes):
                    if tableindex != None:
                        resultsrow[4] = tds[tableindex].text
                    if playerindex != None:
                        resultsrow[5] = tds[playerindex].text
                    if playercountryindex != None:
                        resultsrow[7] = tds[playercountryindex].text
                    if resultindex != None:
                        resultsrow[8] = tds[resultindex].text
                    if opponentindex != None:
                        resultsrow[9] = tds[opponentindex].text
                    if opponentcountryindex != None:
                        resultsrow[11] = tds[opponentcountryindex].text
                    #process names to pull out country data
                    if isplayer:
                        processName(resultsrow)
                    else:
                        resultsrow[6] = 'TEAM EVENT'
                        resultsrow[10] = 'TEAM EVENT'
                    #process country to only have letters
                    resultsrow[7] = re.sub('[^a-zA-Z]','',resultsrow[7])
                    resultsrow[11] = re.sub('[^a-zA-Z]','',resultsrow[11])
                    #check if result is BYE, and put it in the Opponent Last Name, clear first name
                    if re.search('bye', resultsrow[8], re.I):
                        resultsrow[8] = ''
                        resultsrow[9] = ''
                        resultsrow[10] = 'BYE'
                    #remove beginning and ending whitespace
                    resultsrow = [resultrow.strip() for resultrow in resultsrow]
                    playerHistoryToDB(resultsrow)
        else:
            errorresults = ['']*12
            errorresults[0] = eventtype
            errorresults[1] = eventname
            errorresults[2] = date
            errorresults[3] = round
            playerHistoryToDB(errorresults)
    else:
        #if the page doesnt exist
        errorresults = ['']*12
        errorresults[0] = eventtype
        errorresults[1] = eventname
        errorresults[2] = date
        errorresults[3] = round
        playerHistoryToDB(errorresults)

def getAllResults(loop, startround, endround, eventurl, eventtype, eventname, date):
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
                for resulturl in resultsurls:
                    if(resulturl['href'].find("magic.wizards.com") == -1):
                        resulturl['href'] = urlparse.urljoin(eventurl, resulturl['href'])
                    print resulturl['href']
                    if not (re.search('player', resulturl.text, re.I)):
                        if(re.search('(\d+)', resulturl.text)):
                            round = re.search('(\d+)', resulturl.text).group(1)
                        else:
                            round = resulturl.text
                        if not (resulturl['href'] == None or eventname == None or round == None):
                            results = saveResults(loop, resulturl['href'], eventtype, eventname, date, round)
    elif soup.findAll('a', text=re.compile('(result)|(results)', re.I)):
        #if we never found a section where results were all organized, look for links with the word "results" on the page
        resultsurls = soup.findAll('a', text=re.compile('(result)|(results)', re.I))
        #only look at results specified
        
    resultslength = len(resultsurls)
    if endround == 0:
        endround = resultslength
    loop = startround
    while (loop < resultslength and loop < endround):
        if(resulturl['href'].find("magic.wizards.com") == -1):
            resulturl['href'] = urlparse.urljoin(eventurl, resulturl['href'])
        print resulturl['href']
        if not (re.search('player', resulturl.text, re.I)):
            if (re.search('round-(\d+)',resulturl['href'])):
                round = re.search('round-(\d+)',resulturl['href']).group(1)
            else:
                round = ''
            if not (resulturl['href'] == None or eventname == None or round == None):
                results = saveResults(loop, resulturl['href'], eventtype, eventname, date, round)
        #iterate loop
        loop = loop + 1
    else:
        #if nothing useful on the page
        errorresults = ['']*12
        errorresults[0] = eventtype
        errorresults[1] = eventname
        errorresults[2] = date
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

def getAllCoverageEvents(startcoverage=0,endcoverage=0,startround=0,endround=0,startrow=0,endrow=0):
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
        print 'Loop :', loop
        if (endcoverage < loop):
            print "Ending Loop"
            break;
        #grab the loop we are on
        section = sections[loop]

        season = section.find('h2')
        print season
        eventtype=""
        eventname=""
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
                    getAllResults(loop, startround,endround, eventurl, eventtype, eventname, date)
                    
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
                    getAllResults(loop, startround,endround, eventurl, eventtype, eventname, date)
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
                    getAllResults(loop, startround,endround, eventurl, eventtype, eventname, date)
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
                        getAllResults(loop, startround,endround, eventurl, eventtype, eventname, date)
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
                    getAllResults(loop, startround,endround, eventurl, eventtype, eventname, date)
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
                    getAllResults(loop, startround,endround, eventurl, eventtype, eventname, date)
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
                    getAllResults(loop, startround,endround, eventurl, eventtype, eventname, date)
        #iterate the loop
        loop = loop + 1



def getAllCoverageEventsOLD():
    coverageURL = "http://magic.wizards.com/en/events/coverage"
    htmlFile = urllib.urlopen(coverageURL)
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML)
    
    sections = soup.findAll('div', attrs={'class':'bean_block bean_block_html bean--wiz-content-html-block '})
    for idx,section in enumerate(sections[1:]):
        season = section.find('h2')
        events = section.findAll('a', attrs={'class':'more'})
        for event in events:
            if(event['href'].find("magic.wizards.com") == -1):
                event['href'] = urlparse.urljoin(htmlFile.geturl(), event['href'])
            eventname = season.text + ": " + event.text
            print eventname
        getAllResults(event['href'], eventname)