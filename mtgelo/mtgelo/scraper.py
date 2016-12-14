import urllib
from bs4 import BeautifulSoup
import re
import urlparse

from database import *

def saveResults(eventURL, eventname, round):
    htmlFile = urllib.urlopen(eventURL)
    eventURL = htmlFile.geturl()

    try:
        #regular expression for YYYY-MM-DD, looking in the URL, but may want to try and find a better way in the future.
        date = re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", eventURL).group(1)
    except:
        date = "N/A (Parse Error)"
    #some pages do not exist... #wizardProblems
    if (htmlFile.getcode() == 200):
        
        rawHTML = htmlFile.read()
        soup = BeautifulSoup(rawHTML)
        #need to make this better, but this is currently how we determine day 1/2... 
        try:
            #sometimes round is a "string" rather than a number (like Finals, SemiFinals...)
            if (int(round) < 10):
                day = "1";
            else:
                day = "2";
        except:
            day = "N/A (Parse Error)"
        table = soup.findAll('tr')
        totalresults = []
        for row in table[1:]: #skip first row, which is a header row
            tds = row.findAll('td')
            resultsrow = [eventname,day,date,round]
            for td in tds:
                resultsrow.append(td.text)
            #print resultsrow
            #not all tables are the same, some missing country data
            if(len(resultsrow) != 11):
                if(len(resultsrow) == 9):
                    #assuming that country data is missing
                    resultsrow.insert(6, "N/A (Not Provided)")
                    resultsrow.insert(10, "N/A (Not Provided)")
            totalresults.append(resultsrow)
        #print totalresults
        return totalresults
    else:
        #if the page doesnt exist
        errorresults = [[eventname, round, date, "N/A (404)", "N/A (404)", "N/A (404)", "N/A (404)", "N/A (404)", "N/A (404)", "N/A (404)", "N/A (404)"]]
        print errorresults
        return errorresults

def getAllResults(eventURL, eventtype, eventname):
    #eventURL = 'http://magic.wizards.com/en/events/coverage/1994wc'
    if(eventURL.find("magic.wizards.com") == -1):
        eventURL = urlparse.urljoin('http://magic.wizards.com/en/events/coverage', eventURL)
    htmlFile = urllib.urlopen(eventURL)
    eventURL = htmlFile.geturl()
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML)

    print eventURL

    #event page has a section with "by-day" class
    bydays = soup.findAll('div', attrs={"class": "by-day"})
    if (len(bydays) == 0):
        #if it has no "by-day" then look for class "results"... dunno if this works everywhere
        bydays = soup.findAll('div', attrs={"class": "results"})
    for byday in bydays:
        if byday.find('p', text=re.compile("results", flags=re.ignorecase)):
            resultsurls = byday.findAll("a")
            for resulturl in resultsurls:
                if(resulturl['href'].find("magic.wizards.com") == -1):
                    resulturl['href'] = urlparse.urljoin(eventurl, resulturl['href'])
                print resulturl['href']
                try:
                    round = re.search('(\d+)', resulturl.text).group(1)
                except:
                    round = resulturl.text
                results = saveresults(resulturl['href'], eventname, round)
                #print results
                #some more error handling, like when the page has nothing in it
                try:
                    lengthofresults = len(results[0])
                except:
                    lengthofresults = 0
                if(lengthofresults == 11):
                    playerhistorytodb(results)
                else:
                    errorresults = [[eventname, round, "n/a (wrong size)", "n/a (wrong size)", "n/a (wrong size)", "n/a (wrong size)", "n/a (wrong size)", "n/a (wrong size)", "n/a (wrong size)", "n/a (wrong size)", "n/a (wrong size)"]]
                    playerhistorytodb(errorresults)

def getAllCoverageEvents():
    coverageURL = "http://magic.wizards.com/en/events/coverage"
    htmlFile = urllib.urlopen(coverageURL)
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML)
    
    sections = soup.findAll('div', attrs={'class':'bean_block bean_block_html bean--wiz-content-html-block '})
    for loop,section in enumerate(reversed(sections)):
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
                    #print eventurl, eventtype, eventname
                    getAllResults(eventurl, eventtype, eventname)
                    
        #2009 Season
        elif (loop == 15):
            eventtypes = section.findAll('p')
            for eventtypeelem in eventtypes:
                eventtype = eventtypeelem.find('b').text
                eventnames = eventtypeelem.findAll('a')
                for eventnamehtml in eventnames:
                    eventname = eventnamehtml.text
                    eventurl = eventnamehtml['href']
                    #print eventurl, eventtype, eventname
                    getAllResults(eventurl, eventtype, eventname)
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
                    #print eventurl, eventtype, eventname
                    getAllResults(eventurl, eventtype, eventname)
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
                        #print eventurl, eventtype, eventname
                        getAllResults(eventurl, eventtype, eventname)
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
                    #print eventurl, eventtype, eventname
                    getAllResults(eventurl, eventtype, eventname)
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
                    #print eventurl, eventtype, eventname
                    getAllResults(eventurl, eventtype, eventname)
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
                    #print eventurl, eventtype, eventname
                    getAllResults(eventurl, eventtype, eventname)



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