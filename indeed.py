#!/usr/bin/env python
"""
indeed.py
Hacked from Brian Boates's Skillrankapp

Scrape job postings for a given query from
Indeed.com using the search api for key skills
analysis. Also includes Indeed.com specific 
threading functions.

"""
import os, sys, re , urllib2
from Queue import Queue

def getURL(url):
    """
    return: raw text from URL as a string
    params:
            url: string | url to retrieve data from
    """
    response=urllib2.urlopen(url)
    page=response.read()
    #print page
    response.close()
    return page

def getJobURLs(jobQuery, nURLs=1, start=0):
    """
    return: list of strings (each string is a URL to an
            Indeed.com job posting for "jobQuery")
    params:
         jobQuery: string | search terms for Indeed.com
                            (preprocessed for +'s rather than spaces, etc.)
            nURLs: int | number of job posting URL's to return
            start: int | beginning index for api job search
    """
    # pre-process job query
    jobQuery = jobQuery.strip().lower().replace(' ','+')
    
    # list for all URL's to be stored
    allurls = []
    
    # loop through each page of 20 job postings for jobQuery
    for i in range(nURLs//10+1):
        
        print 'url retrieval =', len(allurls)/float(nURLs)*100.0, 'percent complete'
        
        # api link for 10 postings for jobQuery at a time
        api  = 'http://api.indeed.com/ads/apisearch?publisher=6583443037887554&v=2'
         api += '&q=\"'+jobQuery+'\"&start='+str(start + i*10)
    
        # get the content from api URL
        raw = getURL(api)
        
        # parse the raw data for individual job URL's
        urls = re.findall(r'<url>.*</url>', raw)
        
        # remove the <link> and </link> tags from URL's
        urls = [u.replace('<url>','').replace('</url>','') for u in urls]
        
        # append current page of URL's to list of "all" URL's
        allurls += urls
    
    # return only up to nURLs number of URL's for job postings
    return allurls[:nURLs]


def jdClean(jd):
    """
    Clean and "tokenize" a job description using regular expressions
    
    return: processed/cleaned job description
    params:
        jd: string | a string containing an entire "J"ob "D"escription
    """
    # remove remnant mark-up
    jd = re.sub(r'<\w+>', ' ', jd)
    jd = re.sub(r'</\w+>', ' ', jd)
    jd = re.sub(r'<\w+/>', ' ', jd)
    
    # prevent stranded t's and s's from words like don't and client's
    jd = re.sub(r"'\w\s", ' ', jd)
    
    # remove weird apostrophe characters
    jd = re.sub('\\xe2\\x80\\x99\w', '', jd)
    
    # find all occurences of ' wordPUNCTUATIONword ' to "fix"
    fix = re.findall(r'\s\w+[^\w\s]\w+\s', jd)
    for term in fix:
        punc = re.search(r'[^\w\s]', term).group()
        if punc == '/' or punc == ',':
            # replace "/" or "," with an "and"
            jd = jd.replace(punc,' and ')
        else:
            jd = jd.replace(term, term.replace(punc,''))
         
    # convert unwanted punctuation into spaces (keep +'s)
    jd = re.sub('[^A-Za-z0-9\s\+\#-]+', ' ', jd)
    
    # remove all upper-case letters
    jd = jd.lower()
    
    # remove pure numbers
    jd = re.sub(r'\s\d+\s', ' ', jd)
    
    # remove pure puncuations
    jd = re.sub(r'\s[\+\#-]+\s', ' ', jd)
    
    # only keep one-letter words that are C or R
    Nr = jd.split().count('r')
    Nc = jd.split().count('c')    
    fix = re.findall(r'\w\w+', jd)
    jdnew = ''
    for f in fix: jdnew += f+' '
    for i in range(Nr): jdnew += 'r '
    for i in range(Nc): jdnew += 'c '
    jd = jdnew
#    jd = re.sub(r'\s[^CR]\s',' ', jd)
    
    # fix "html css" bigrams / get rid of them
    jd = re.sub(r'html\s+css','html and css', jd)
    
    # remaining hacks
    jd = jd.replace('objectoriented','object oriented')
    jd = jd.replace('java script','javascript')
    jd = jd.replace(' js ',' javascript ')
    jd = jd.replace('css3','css')
    
    return jd


def parseJobPosting(url):
    """
    return: jobkey[string], position[string], company[string], 
                            location[string], words[list of strings]
    params:
            url: string | url for the job posting to parse
    """
    # extract raw data from URL and remove returns

    raw = getURL(url)

    raw = raw.replace('\n',' ')


    # retrieve the jobkey from the url
    jobkey = re.search(r'jk=\w+&amp', url).group().replace('jk=','').replace('&amp','')
    
    # extract job position
    try:
        position = re.search(r'<title>.*</title>', raw).group()
        # position = re.search(r'>\w.*\-.*\-.*\|', position).group()
        position = re.search(r'>\w.*\-.*\|', position).group()
        position = position.replace('>','').replace('|','').split('-')[0].replace('job','').strip()
    except AttributeError:
        position = 'Unknown'
        
    # retrieve job location
    try:
        location = re.search(r'<span class="location">.*?<span class="summary">', raw).group()
        location = re.search(r'<span class="location">.*?</span>', location).group()
        location = location.replace('<span class="location">','').replace('</span>','')
    except AttributeError:
        location = 'Unknown'
    
    # receive job's company
    try:
        company = re.search(r'<span class="company">.*?<span class="summary">', raw).group()
        company = company.split('</span>')[0].split('>')[-1]
    except AttributeError:
        company = 'Unknown'
    
    # retrieve the job description section
    try:
        start = 'span class="summary"'
        end = 'days ago'
        end   = '<span class="sdn">'#+company
        #jd = re.search(r''+start+'.*'+end+'.*'+'days ago', raw,re.IGNORECASE).group()
        jd = re.search(r''+start+'.*?'+end, raw).group()
        jd = jd.replace('span class="summary"','').replace('<span class="sdn">','')
        jd = jd.replace('<span class="date">',' ').replace('days ago',' ')
    except AttributeError:
        jd = ''
    
    # more advanced processing/cleaning of the job description
    words = jdClean(jd).split() # list of words
    discard=['a','an','the','and']
    words=','.join([x for x in words if x not in discard])
    return (jobkey, position, company, location, words)



if __name__=="__main__":
    url=getJobURLs('data scientist',nURLs=2)
    for x in url:
       print parseJobPosting(x)
