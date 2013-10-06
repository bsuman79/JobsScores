"""
Author: Suman Bhattacharya
reads the joblist for a particular field and the user profile then rank the job postings for the user, gives a score from 0-100.

"""
import MySQLdb as mdb
import sys
import itertools
import re
from collections import defaultdict

class AnalyzeJobComp:
  def analyzejobcomp(self,id='',searchterm='',db='jobdb',table1name='jobcomp',table2name='indeed',table3name='userdata',table4name='searchwords'):
      try:
          if db=='jobdb':  
              con = mdb.connect('localhost', 'mysqlu','',db); # use this for local
          else:
              con = mdb.connect('remote host', 'username','passwd');
          cur = con.cursor()
          cur.execute("use %s"%(db))
          # read the user data
          cur.execute("select uId,firstname,lastname,summary,positions,educations,projects,skills from %s where uId='%s'"%(table3name,id))
          userdata=cur.fetchall()
          # string up the summary, skills, etc.
          summary=list(set([x for x in userdata[0][3].split()]))
          skills=list([item for sublist in [y.split() for y in [x for x in userdata[0][7].split(',')]] for item in sublist])
          educations= list([item for sublist in [y.split() for y in [x for x in userdata[0][5].split(',')]] for item in sublist])
          positions=list([item for sublist in [y.split() for y in [x for x in userdata[0][4].split(',')]] for item in sublist])
          words=[element.lower() for element in list(itertools.chain(summary,skills,educations,positions))]
          
          words=[w.replace('-',',') for w in words]
          words=','.join([re.sub(r'[^\w++,]','',w) for w in words])
          # get job data
          cur.execute("select jc.impwords,i.title,i.company,i.location,i.description from %s as jc inner join %s as i on jc.Id=i.Id where jc.searchterm LIKE '%s'"%(table1name,table2name,searchterm))
          jobdata=cur.fetchall()

          output=[]
          for i in xrange(len(jobdata)):
              impwords=[]
              # important words that are not bigrams
              row2=list(set([element for element in jobdata[i][0].split(',')  if '-' not in element]))
              # important bigram words
              row3=list(set([element.replace('-',',') for element in jobdata[i][0].split(',') if '-' in element]))
              [impwords.append(w) for w in jobdata[i][0].split(',')]
              #print row3,words
              # for each job posting, find the important words that are in the posting and in the profile
              wordselect= list(set([x.group(0).replace(',','-') for x in [re.search(r'\b%s\b' %x,words) for x in row3] if x] + [x.group(0) for x in [re.search(r'\b%s\b' %x,words) for x in row2] if x])) 
              # some hacks to remove
              if 'sci' in wordselect: wordselect.remove('sci')
              if 'sci' in impwords: impwords.remove('sci')
              if 'efi' in wordselect: wordselect.remove('efi')
              if 'efi' in impwords: impwords.remove('efi')
              #print wordselect,impwords
              output.append((wordselect,impwords,len(wordselect)*1.0/len(impwords),jobdata[i][1],jobdata[i][2],jobdata[i][3],jobdata[i][4]))
          # get the weightage of all the words for a searchterm.
          cur.execute("select words,counts*ratio from %s where searchterm='%s'"%(table4name,searchterm))
          rows=cur.fetchall()
          search_words=defaultdict(float)
          for row in rows:
             search_words[row[0]]=row[1]
          #print search_words    
      except mdb.Error, e:
          print "Error %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)
      finally:
        if cur: cur.close()
        if con: con.close()
        return output,search_words,userdata[0][1]


