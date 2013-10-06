"""
Author: Suman Bhattacharya

create the local/remote database that store user and the job related data

"""

import MySQLdb as mdb
import sys
import indeed
import re
from linkedin.linkedin import  (LinkedInAuthentication, LinkedInDeveloperAuthentication,LinkedInApplication, PERMISSIONS)
#from collections import defaultdict
#import json
class jobdatabase:
   def createdb(self,db='jobdb'):
     try:
        con = mdb.connect('localhost', 'mysqlu','');
        cur = con.cursor()
        cur.execute("create database if not exists %s"%(db))
     except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
     finally:
        if cur: cur.close()
        if con: con.close()
   # create table to store the job listing from indeed
   def filluptable(self,searchterm,itemlist,case,tablename='indeed',db='jobdb'): 
      try:
          con = mdb.connect('localhost', 'mysqlu','',db);
          cur = con.cursor()
          cur.execute("use %s"%(db))
          if case=='start':
             cur.execute('drop table if exists '+tablename)
             cur.execute( 'create table if not exists '+tablename+' (Id varchar(100) PRIMARY KEY, searchterm text, title text,company text,location text,description text)')
             for item in itemlist:
                #print item[0],searchterm,item[1],item[2],item[3],item[4]
                cur.execute("INSERT INTO "+tablename+" (Id, searchterm,title,company,location,description) VALUES('%s','%s','%s','%s','%s','%s')"%(item[0],searchterm,item[1],item[2],item[3],item[4]))
          if case=='repeat':
             for item in itemlist:
                #print item[0],searchterm,item[1],item[2],item[3],item[4]
                cur.execute("INSERT INTO "+tablename+" (Id, searchterm,title,company,location,description) VALUES('%s','%s','%s','%s','%s','%s')"%(item[0],searchterm,item[1],item[2],item[3],item[4]))         
      except mdb.Error, e:
        #print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
      finally:
        if cur: cur.close()
        if con: con.close()
   # store the important words for a particular search term
   def searchwordsdb(self,searchterm,itemlist,case,tablename='searchwords',db='jobdb'):
      try:
          con = mdb.connect('localhost', 'mysqlu','',db);
          cur = con.cursor()
          cur.execute("use %s"%(db))
          if case=='start':
             cur.execute('drop table if exists '+tablename)
             cur.execute( 'create table if not exists '+tablename+' (Id int primary key auto_increment,searchterm varchar(200),words varchar(100),counts int,ratio float)')
             for key in itemlist.keys():
                cur.execute("INSERT INTO "+tablename+" (searchterm,words,counts,ratio) VALUES('%s','%s','%d','%f')"%(searchterm,key,itemlist[key][1],itemlist[key][0]))
          if case=='repeat':
             for key in itemlist.keys():
                cur.execute("REPLACE INTO "+tablename+" (searchterm,words,counts,ratio) VALUES('%s','%s','%d','%f')"%(searchterm,key,itemlist[key][1],itemlist[key][0]))
      except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
      finally:
        if cur: cur.close()
        if con: con.close()   
               
   # compare each job posting and include the important words for each posting
   def jobcompatdb(self,tablename='indeed',table1name='searchwords',table2name='jobcomp',db='jobdb',searchterm=''):
      try:
          con = mdb.connect('localhost', 'mysqlu','',db);
          cur = con.cursor()
          cur.execute("use %s"%(db))
          cur.execute("select words from "+table1name+" where searchterm LIKE '"+searchterm+"'")
          rows1=cur.fetchall()
          totwords=float(len(rows1))
          rows2=list(set([element for tupl in rows1 for element in tupl if '-' not in element]))
          rows3=list(set([element.replace('-',',') for tupl in rows1 for element in tupl if '-' in element]))
      
          cur.execute("select Id,description FROM %s where searchterm LIKE '%s';"%(tablename,searchterm))
          rows=cur.fetchall()
          cur.execute( 'create table if not exists %s (Id varchar(100) primary key,searchterm varchar(100),impwords text,jobratio float)'%(table2name))
          for row in rows:
             #print row[1]            
             words=list(set([x.group(0).replace(',','-') for x in [re.search(x,row[1]) for x in rows3] if x] +[w for w in rows2 if w in row[1].split(',')]))
             #[x.group(0) for x in [re.search(x,row[1]) for x in rows2] if x]))
             #print words,set(words)
             lenwords=len(words)
             impwords=','.join([word for word in words])
             cur.execute("REPLACE INTO %s (Id,searchterm,impwords,jobratio) VALUES('%s','%s','%s','%f')"%(table2name,row[0],searchterm,impwords,lenwords/totwords))
             #print row[0],words
      except mdb.Error, e:
          print "Error %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)
      finally:
        if cur: cur.close()
        if con: con.close()
   # use your developer credential to get Linkedin profile of users   
   def getLinkedinProf(self,user_key,user_secret):
        API_KEY = 'your key'
        API_SECRET = 'your secret'
        RETURN_URL = 'http://127.0.0.1:5000/' 
        USER_KEY= user_key 
        USER_SECRET=user_secret 
        authentication = LinkedInDeveloperAuthentication(API_KEY, API_SECRET, USER_KEY,USER_SECRET,RETURN_URL, PERMISSIONS.enums.values()) #developer as user

        application = LinkedInApplication(authentication)
        selectors=['id', 'first-name', 'last-name', 'location', 'distance', 'num-connections', 'skills', 'educations','summary','positions','projects','connections']
        return selectors,application.get_profile(selectors=selectors)
   #  store user information, mainly positions projects. educations, skills
   def storeUProf(self,prof,tablename='userdata',db='jobdb'): 
      #print prof[u'summary'] 
      positions,projects,educations,skills=[],[],[],[]
      if "positions" in prof.keys():
          num= prof[u'positions'][u'_total']
          for i in xrange(num):
            try: 
               positions.extend([prof[u'positions'][u'values'][i][u'title'],prof[u'positions'][u'values'][i][u'company'][u'industry'],prof[u'positions'][u'values'][i][u'company'][u'name'],prof[u'positions'][u'values'][i][u'summary']])
            except KeyError:
               continue
          positions=','.join([x for x in set(positions)]).replace("'","")
      if "projects" in prof.keys():
          num=prof[u'projects'][u'_total']
          for i in xrange(num):
             try:
               projects.extend([prof[u'projects'][u'values'][i][u'name']])
             except KeyError:
               continue
          projects=','.join([x for x in set(projects)]).replace("'","")
      if "educations" in prof.keys():
          num=prof[u'educations'][u'_total']
          for i in xrange(num):
            try:
              educations.extend([prof[u'educations'][u'values'][i][u'degree'],prof[u'educations'][u'values'][i][u'schoolName'],prof[u'educations'][u'values'][i][u'fieldOfStudy']])
            except KeyError:
               continue
          educations= ','.join([x for x in set(educations)]).replace("'","")
      if "skills" in prof.keys():
         num= prof[u'skills'][u'_total']
         for i in xrange(num):
           try:
              skills.extend([prof[u'skills'][u'values'][i][u'skill'][u'name']])
           except KeyError:
             continue
         skills= ','.join([x for x in set(skills)]).replace("'","")
         uid=prof[u'id'].replace("'","")
         firstname=prof[u'firstName'].replace("'","")
         lastname=prof[u'lastName'].replace("'","")
         summary=prof[u'summary'].replace("'","")
      try:
          if db=='jobdb':
              con = mdb.connect('localhost', 'mysqlu','',db); #use this for local db
          else:
              con = mdb.connect('remote host', 'username','passwd');
          cur = con.cursor()
          cur.execute("use %s"%(db))
          cur.execute( 'create table if not exists %s (uId varchar(100) primary key,firstname varchar (100), lastname varchar(100), summary text,positions text,educations text,projects text, skills text)'%(tablename))
      
          cur.execute("REPLACE INTO %s (uId,firstname,lastname,summary,positions,educations,projects,skills) VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(tablename,uid,firstname.encode('ascii','ignore'),lastname.encode('ascii','ignore'),summary.encode('ascii','ignore'),positions,educations,projects,skills))
      except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
      finally:
        con.commit()
        if cur: cur.close()
        if con: con.close()   

if __name__=="__main__":
    search_term='data scientist'
    """
    url=indeed.getJobURLs(searchterm,nURLs=1000,start=0)
    itemlist=[]
    for x in url:
        itemlist.append(indeed.parseJobPosting(x))
        if len(itemlist)//100.0: print 'posting read = ', len(itemlist)/float(len(url))*100.0, 'percent complete'
    """
    jdb=jobdatabase()
    #jdb.createdb()
    #print 'total= ',len(itemlist)
    #jdb.filluptable(searchterm,itemlist,'repeat')
    #jdb.jobcompatdb(searchterm=search_term)
    user_key= ''
    user_secret=''
    fields,prof=jdb.getLinkedinProf(user_key,user_secret)
    #print fields,prof
    jdb.storeUProf(prof)
    
