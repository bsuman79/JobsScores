"""
Author: Suman Bhattacharya

transfer the data from local mysql database to heroku (cleardb) mysql database.

"""
import MySQLdb as mdb
import sys

def transferData(tablename,items):
   try:
       con = mdb.connect('cleardb host name', 'cleardb username','cleardb passwd');
       cur = con.cursor()
       cur.execute("use database name")

       if tablename=="table1":
            cur.execute( 'create table if not exists '+tablename+' (Id varchar(100) PRIMARY KEY, searchterm text, title text,company text,location text,description text)')
            for item in items:
                cur.execute("replace into %s (Id, searchterm,title,company,location,description) VALUES('%s','%s','%s','%s','%s','%s')"%(tablename,item[0],item[1],item[2],item[3],item[4],item[5]))

       if tablename=="table2":
             cur.execute( 'create table if not exists %s (Id varchar(100) primary key,searchterm varchar(100),impwords text,jobratio float)'%(tablename))
             for item in items:
                cur.execute("REPLACE INTO %s (Id,searchterm,impwords,jobratio) VALUES('%s','%s','%s','%f')"%(tablename,item[0],item[1],item[2],item[3]))

       if tablename=="table3":
             cur.execute( 'create table if not exists '+tablename+' (Id int primary key auto_increment,searchterm varchar(200),words varchar(100),counts int,ratio float)')
             for item in items:
                 cur.execute("REPLACE INTO %s (searchterm,words,counts,ratio) VALUES('%s','%s','%d','%f')"%(tablename,item[1],item[2],item[3],item[4]))

       if tablename=="table4":
             cur.execute( 'create table if not exists %s (uId varchar(100) primary key,firstname varchar (100), lastname varchar(100), summary text,positions text,educations text,projects text, skills text)'%(tablename))
             for item in items:
                   cur.execute("REPLACE INTO %s (uId,firstname,lastname,summary,positions,educations,projects,skills) VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(tablename,item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7]))

   except (AttributeError, mdb.OperationalError), e:
       print "Error %d: %s" % (e.args[0],e.args[1])
       sys.exit(1)
   finally:
       con.commit()
       if cur: cur.close()
       if con: con.close()

def localData(tablename, db='local database name'):
      try:
          con = mdb.connect('localhost', 'username','passwd',db);
          cur = con.cursor()
          cur.execute("use %s"%(db))
          cur.execute("show tables")
          items=cur.fetchall()

          cur.execute("select * from %s"%(tablename))
          items=cur.fetchall()
          cur.execute("describe %s"%(tablename))
          header=cur.fetchall()
 
      except mdb.Error, e:
        #print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
      finally:
        if cur: cur.close()
        if con: con.close()
      return items,header
if __name__=="__main__":
  tables=['table1','table2','table3','table4']
  for tablename in tables:
     items,header=localData(tablename) 
     transferData(tablename, items)

  #print header
