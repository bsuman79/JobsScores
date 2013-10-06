"""
Author: Suman Bhattacharya
reads the job postings, find the important words for the searchterm ie find out the words that appear in the job postings for the searchterm more often than a background job set containing various postings.

"""
import MySQLdb as mdb
import sys
import re
from collections import defaultdict,OrderedDict,Counter
from itertools import islice
import nltk 
from nltk.collocations import *
import math
from operator import itemgetter
from nltk import pos_tag, word_tokenize
import removewords
import createjobdb
import time
def analyzetable(table='indeed',db='jobdb',searchterm=''):      
      try:
        con = mdb.connect('localhost', 'mysqlu','',db);
        cur = con.cursor()
        cur.execute("use %s"%(db))
        if searchterm=='': 
          # reads the postings for all jobs
          cur.execute("select description from "+table)
        else:
             print searchterm
             # read the posting for the searchterm
             cur.execute("select description from "+table+" where searchterm LIKE '"+searchterm+"'")
        numrows= int(cur.rowcount)
        words=[]
        rows=cur.fetchall()
        # we have created the removewords (like 'the', 'with') , remove them from the posting, then create a list of words from the posings
        [[[words.append(xx) for xx in x.split(',') if xx not in removewords.remove_words] for x in row] for row in rows]   
      except mdb.Error, e:
          print "Error %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)
      finally:
        if cur: cur.close()
        if con: con.close()
      return words,numrows
# count the number of occurence of each word
def countwordsnum(words):        
        result = defaultdict(int)
        for word in words:
            result[word] += 1
        return result
# find bigram
def bigram(words):
   out= nltk.bigrams(words) 
   freq= nltk.FreqDist(out)  
   result=defaultdict(int)
   for key,val in freq.items():
         keys="-".join([k for k in key])
         result[keys]=val
   return result
# delete bigram from the 'one' word list to avoid double counting
def del_bigram_from_words(bi_keys):
   words=[]
   for k in bi_keys:
      w1,w2=k.split('-')
      words.append(w1)
      words.append(w2)
   return list(set(words))    

def main(search_term=''):
    # get the words in all the postings, call in 'background'
    words,numrows=analyzetable()
    print numrows
    tot_words_bck=len(words)
    # create a dict of words and the occurence of each word
    wordnum=countwordsnum(words)
    tstart=time.time()

    #print wordnum['hadoop'],wordnum['java'],wordnum['learning'],wordnum['c++'],wordnum['python'],wordnum['excel'],wordnum['hive'],wordnum['pig'],wordnum['mysql'],wordnum['phd']

   # do the above for a particular searchterm
    words1,numrows1=analyzetable(searchterm=search_term)
    tot_words_search= len(words1)
    wordnum1=countwordsnum(words1)
    print len(wordnum),len(wordnum1),numrows1
    t=time.time()
    print t-tstart
    # remove the words both from the background nd the search list that occur too few or too many times in the background list
    for key in wordnum.keys():
      if wordnum[key]<=1 or wordnum[key]>numrows/2.0:
         del wordnum[key]           
         if key in wordnum1.keys() or wordnum1[key]<=2: del wordnum1[key]

    tot_words_bck,tot_words_search=len(wordnum),len(wordnum1)
    print tot_words_bck,tot_words_search
    # keep the words that occur a certain number of times and also occur x-times more in search list compared to the background list
    wordratio=defaultdict(float)
    for key in wordnum1.keys():
      ratio=float(wordnum1[key])/wordnum[key]*float(numrows)/numrows1 #*tot_words_bck/float(tot_words_search) 
      if ratio>1.1 and wordnum1[key]>0.4*numrows1: wordratio[key]=(ratio,wordnum1[key])
      elif ratio>2.4 and wordnum1[key]>0.1*numrows1 and wordnum1[key]<=0.4*numrows1: wordratio[key]=(ratio,wordnum1[key])
      elif ratio>4 and wordnum1[key]<=0.1*numrows1 and wordnum1[key]>0.05*numrows1: wordratio[key]=(ratio,wordnum1[key])

    #print len(wordnum1),len(wordratio),wordratio['java'],wordnum1['java'],wordnum['java']
    print len(wordratio.items())
    bigramwords=bigram(words)
    t2=time.time()     
    print t2-t
    bigramwords1=bigram(words1)
    t3= time.time()
    print t3-t2

    bigramratio=defaultdict(float)
    for key,val in bigramwords1.items():
        ratio=float(val)/bigramwords[key]*float(numrows)/numrows1
        if val>0.1*numrows1 and val<numrows1 and ratio>2.0: bigramratio[key]=(ratio,val)
    # if bigram words also in single words then del single words
    wordstodel=del_bigram_from_words(bigramratio.keys())
    for key in wordstodel:
       if key in wordratio.keys(): del wordratio[key]
    for key in bigramratio.keys():
        k1,k2= key.split('-')
        if k1==k2:
            bigramratio[k1]=bigramratio[key]
            del bigramratio[key] 
        key1=k1+k2
        if key1 in wordratio.keys():
          bigramratio[key]=tuple(map(lambda x, y: x + y, bigramratio[key], wordratio[key1]))
          del wordratio[key1]

    wordratio.update(bigramratio)
    # add plural words to sngular and delete plural
    keys1=[(key[:-1],key) for key in wordratio.keys()]
    for key in keys1:
       if key[0] in wordratio.keys():
          print key[0],key[1]
          wordratio[key[0]]=tuple(map(lambda x, y: x + y, wordratio[key[0]], wordratio[key[1]]))
          del wordratio[key[1]]
    for key in removewords.remove_search_words: 
     if key in wordratio.keys():
       del wordratio[key]
   
            
    print len(wordratio.items())
    # sort the important words by weightage, then put them in the database, this form the list of important words for that search term
    res= OrderedDict(sorted(wordratio.items(),key=lambda x: x[1][1]))
    createjobdb.jobdatabase().searchwordsdb(search_term,wordratio,'repeat')
    print list(res)[-50:]
    print time.time()-t3
    print time.time()-tstart

if __name__=="__main__":
    #import profile
    #profile.run('main()') 
    searchterm='software engineer'
    main(search_term=searchterm)



