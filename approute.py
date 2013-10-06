"""
Author: Suman Bhattacharya

the Flask routine that render the html pages and get the results from the database

"""


from flask import Flask, render_template,url_for,session
from flask import request, jsonify
from collections import OrderedDict,defaultdict
import os
#import numpy as np
import analyzejobcomp, createjobdb
from operator import itemgetter
import math
import oauth2 as oauth
import urlparse, webbrowser


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__,template_folder=tmpl_dir)
app.config.update(
    DEBUG = True,
)
app.secret_key = 'xxx' 

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('homev2.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/howitworks')
def howitworks():
    return render_template('howitworks.html')
# Linkedin oauth1.0 happens in two steps, first using the unique consumer key and secret generate the webpage to direct the user to, then once authenticated, the user enter the 5 digit key 
@app.route('/linkedinAuth', methods=['GET','POST'])
def linkedinAccess():
  consumer_key = 'your key'
  consumer_secret = 'your secret'
  return_url = ' http://0.0.0.0:5000/' 
  request_token_url= 'https://api.linkedin.com/uas/oauth/requestToken'
  access_token_url= 'https://api.linkedin.com/uas/oauth/accessToken'
  authorize_url= 'https://www.linkedin.com/uas/oauth/authenticate'

  val,request_token,consumer=None,{},''

  try: 
    val= request.form['linkprof']
  except KeyError:
    try:
      val=request.form['linkcode']
      #print val
    except KeyError:
      exit()

  # this part generate the webpage to direct the user to
  if val=="linkedinauth":     
       consumer = oauth.Consumer(consumer_key, consumer_secret)
       client = oauth.Client(consumer)
       resp, content = client.request(request_token_url, "POST")
       if resp['status'] != '200':
         raise Exception("Invalid response %s." % resp['status'])
       request_token= dict(urlparse.parse_qsl(content))
 
       session['request_token']=request_token
       session['consumer']=consumer

       url= "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
       print "Go to the following link in your browser:",url     
       return url
  # this part enter the 5 digit key which is then used to get the profile informatin
  if len(val)<=5:
         oauth_verifier = val
         print oauth_verifier
         request_token=session['request_token']
         consumer=session['consumer']
         token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
         token.set_verifier(oauth_verifier)

         client = oauth.Client(consumer, token)
         resp, content = client.request(access_token_url, "POST")
         access_token = dict(urlparse.parse_qsl(content))
         print access_token 
         try:
            user_key=access_token['oauth_token']
            user_secret=access_token['oauth_token_secret']
         except KeyError:
            return "tryagain"
         fields,prof=createjobdb.jobdatabase().getLinkedinProf(user_key,user_secret)
         keys=[key for key in prof.keys()]
         print keys
         if "skills" not in keys or "id" not in keys \
         or  "summary" not in keys: 
               return "tryagain1"
         print "users name is ",prof[u'firstName']
         session['id']=prof[u'id']
         createjobdb.jobdatabase().storeUProf(prof,db='database name')
         return "gotit"  
  return  ""  
# the driver routine that manage the user request ie which searchterm to look for, given the request, the routine returns the job list matched to user profile
@app.route('/analyze', methods=['POST'] )
def analyzethis():
      if request.method=="POST":
        search_term = request.form['jobQuery']
        #print search_term 
      ajc=analyzejobcomp.AnalyzeJobComp()
      #try:
      output,search_words,firstname=ajc.analyzejobcomp(id=session['id'],searchterm=search_term,db='databse name')
      #except KeyError:
        #return 'getprofile'
      top20= list(OrderedDict(sorted(search_words.items(),key=lambda x: x[1])))
      #print top20[-20:]

      #matchwords,jobwords,compfact,jobtitle,company,location,jobdescription=[],[],[],[],[],[],[],
      compfactwt,totmatchwords=[],[]  
      dictresults = {'items':[]}
      tmpdict=defaultdict(float)
      for i in xrange(len(output)):
        if output[i][2] != 1:
            sum,sum1=0.0,0.0
            for matchword in output[i][0]:
               totmatchwords.append(matchword)
               if matchword in search_words.keys():
                   sum+=search_words[matchword]
            for jobword in output[i][1]:
               if jobword in search_words.keys():
                  sum1+= search_words[jobword]
            compfactwt.append(sum/sum1)
            tmpdict[(str(" , ".join([x for x in output[i][0]])),str(" , ".join([x for x in output[i][1] if x not in output[i][0]])),str(output[i][3]),str(output[i][4]),str(output[i][5]),str(output[i][6]))]=sum/sum1

      ct=0
      for x in sorted(tmpdict,key=tmpdict.get,reverse=True):
           xx=x[5].split(',')
           #print int(len(xx)*0.1)
           xx=' '.join(xx[:int(len(xx)*0.1)])
           #print xx
           dictresults['items'].append({'matchwords':x[0], 'jobwords':x[1], 'compfact': "{0:.0f}".format(tmpdict[x]*100), 'jobtitle': x[2], 'company': x[3], 'location': x[4], 'jobdescription': xx})
           #print x[0],x[1],x[2],x[3],tmpdict[x]
           ct+=1
           if ct==40 or tmpdict[x]==0: break
      dictresults['top20words']= top20[-20:]
      dictresults['firstname']=firstname
      return jsonify(dictresults)

if __name__ == '__main__':
    port=int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

