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

def getAllResults(eventURL):
    htmlFile = urllib.urlopen(eventURL)
    eventURL = htmlFile.geturl()
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML)

    print eventURL
    try:
        #url can be of the form:
        #http://magic.wizards.com/en/events/coverage/2012pc
        #or
        #http://magic.wizards.com/en/articles/archive/event-coverage/us-nationals-1999-reports-2015-12-18
        #or
        #some other stuff, need to improve this probably
        eventname = eventURL.split("coverage/",1)[1]
    except:
        eventname = "N/A (Parse Error)"
    #modern event page has a section with "by-day" class
    bydays = soup.findAll('div', attrs={"class": "by-day"})
    if (len(bydays) == 0):
        #if it has no "by-day" then look for class "results"... dunno if this works everywhere
        bydays = soup.findAll('div', attrs={"class": "results"})
    for byday in bydays:
        if byday.find('p', text=re.compile("results", flags=re.IGNORECASE)):
            resultsURLs = byday.findAll("a")
            for resultURL in resultsURLs:
                if(resultURL['href'].find("magic.wizards.com") == -1):
                    resultURL['href'] = urlparse.urljoin(eventURL, resultURL['href'])
                print resultURL['href']
                try:
                    round = re.search('(\d+)', resultURL.text).group(1)
                except:
                    round = resultURL.text
                results = saveResults(resultURL['href'], eventname, round)
                #print results
                #some more error handling, like when the page has nothing in it
                try:
                    lengthofresults = len(results[0])
                except:
                    lengthofresults = 0
                if(lengthofresults == 11):
                    playerHistoryToDB(results)
                else:
                    errorresults = [[eventname, round, "N/A (Wrong Size)", "N/A (Wrong Size)", "N/A (Wrong Size)", "N/A (Wrong Size)", "N/A (Wrong Size)", "N/A (Wrong Size)", "N/A (Wrong Size)", "N/A (Wrong Size)", "N/A (Wrong Size)"]]
                    playerHistoryToDB(errorresults)

def getAllCoverageEvents():
    coverageURL = "http://magic.wizards.com/en/events/coverage"
    htmlFile = urllib.urlopen(coverageURL)
    rawHTML = htmlFile.read()
    soup = BeautifulSoup(rawHTML)

    events = soup.findAll('a', attrs={'class':'more'})
    for event in events[133:]: #starting at 133, due to failure at Orlando
        if(event['href'].find("magic.wizards.com") == -1):
            event['href'] = urlparse.urljoin(htmlFile.geturl(), event['href'])
        print event['href']
        getAllResults(event['href'])