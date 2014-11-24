#Autoreply to tweets with a postcode in

from __future__ import print_function
import sys
import twitter
import time
import MySQLdb as mdb
import random
from time import gmtime, strftime

#build data structure for possible retweets
class tweet(object):
    text = None
    idnum = None
    user = None
    reply = None

#outputs what is happening to a log file for debugging
def logger(tolog):
	f = open ('log.txt','a')
	f.write(tolog)

#puts postcode in a standard format
def validatePostcode(text):
	return text.replace('@londonpostcode','').replace(' ','').upper()

#add tweets to the database 
def insertTweet(idnum):
	if idnum != None:
		try:
			#connext to the database as pythonuser
			con = mdb.connect('localhost', 'pythonuser', 'lettersofnote', 'londonData', use_unicode = True);
			#create a cursor to move around the db
			cur = con.cursor()
			#search for the zoneid
			cur.execute('INSERT INTO Tweets VALUE (%d)' % idnum)
			con.commit()
			#print 'Tweet %d inserted.' % idnum
			logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + 'Tweet %d inserted.\n' % idnum)
		
		except mdb.Error, e:
			print("Error %d: %s" % (e.args[0],e.args[1]))
	
		finally:
			if con:
				con.close()

#Return zoneid from postcode
def fetchZoneID(postcode):
	try:
		#connext to the database as pythonuser
		con = mdb.connect('localhost', 'pythonuser', 'lettersofnote', 'londonData', use_unicode = True);
		#create a cursor to move around the db
		cur = con.cursor()
		#search for the zoneid
		cur.execute('SELECT ZONEID FROM PC2ZONEID WHERE Postcode = "%s"' % postcode)
		#print cur.fetchall()
		fetched = cur.fetchall()
		return fetched

	except mdb.Error, e:
		print("Error %d: %s" % (e.args[0],e.args[1]))
		return ''
	
	finally:
		if con:
			con.close() 

#retrieve a fact from the database
def fetchFact(pc,zoneid):
	try:
		#connext to the database as pythonuser
		con = mdb.connect('localhost', 'pythonuser', 'lettersofnote', 'londonData', use_unicode = True);
		#create a cursor to move around the db
		cur = con.cursor()
		#search for the facts
		cur.execute('SELECT Fact FROM PCFacts WHERE PC = "%s" UNION ALL SELECT Fact FROM ZoneFacts WHERE ZONEID = "%s"' % (pc, zoneid))
		fetched = cur.fetchall()
		return fetched

	except mdb.Error, e:
		print("Error %d: %s" % (e.args[0],e.args[1]))
		return ''
	
	finally:
		if con:
			con.close() 

#check if tweets have been replied to 
def checkTweets(tweetid):
	if tweetid != None:
		try:
			#connext to the database as pythonuser
			con = mdb.connect('localhost', 'pythonuser', 'lettersofnote', 'londonData', use_unicode = True);
			#create a cursor to move around the db
			cur = con.cursor()
			#search for the tweetid
			cur.execute('SELECT * FROM Tweets WHERE TweetID = %d' % tweetid)
			fetched = cur.fetchall()
			if len(fetched) > 0:
				return True
			else:
				return False

		except mdb.Error, e:
			print("Error %d: %s" % (e.args[0],e.args[1]))
			return False
		
		finally:
			if con:
				con.close()
	else:
		return False

def main():
    #instatiate python twitter API wrapper
	api = twitter.Api(consumer_key='o3YrWKmZXXI8GcURHlApilBw8', consumer_secret='AHRYjbZp70olGFEdqc7b6Ja5m6y6cNnkHeksrSlR5eTf0MtxXy', access_token_key='2813607432-UE65IkfKaV1O0vIbq2FHX7L1wx39086zynZLl8a', access_token_secret='LFdJBcQefgitJSpD0EL0nYqU3xN0h0I1AHsnMxkWckMyj')

	print('Started')
	#loop for main calls
	while True:
		try:
			print('Running...', end='\r')
			#get mentions for possible reply
			mentions = api.GetMentions()

			#create a list of instances of tweet to store tweets
			tweets = [tweet() for i in mentions]

			#pull data from the mentions and populate the tweets list
			for j,i in enumerate(tweets):
				i.text = mentions[j].text
				i.idnum = mentions[j].id
				i.user = mentions[j].user.screen_name
				i.reply = None
	
			#check to see we have got everything
			#print 'I have found %d tweets' % len(tweets)
			#logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' found %d tweets\n' % len(tweets))
			#print 'recovered tweets'
			#for i in tweets:
			#	print i.text, i.idnum, i.user, i.reply

			#check whether the tweets have been replied to in database
			for i in tweets[:]:
				if checkTweets(i.idnum):
					tweets.remove(i)
					#print '%d has been replied to before' % i.idnum
				#else:
					#print '%d is new' % i.idnum
	
			#check to see we have removed correctly
			#print '%d not replied to' % len(tweets)
			if len(tweets) > 0:
				logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' ' + str(len(tweets)) + ' not replied to:\n')
			#print 'edited tweets'
			for i in tweets:
				#print i.text, i.idnum, i.user, i.reply
				logger(str(i.idnum) + ' ' + str(i.user) + ' ' + str(i.text) + '\n')
	
			#print fetchZoneID('SW21BN')[0][0]
			#print fetchFact('E1')
			#dive into database and get replies for each postcode
			for i in tweets:
				try:
					pc = validatePostcode(i.text)
					zid= fetchZoneID(pc)[0][0]
					facts = fetchFact(pc,zid)
					#print(facts)
				except IndexError:
					facts = ()
				#print 'Got this from database:', facts
				if len(facts) > 0:
					price = facts[-1][0]
					fact = random.choice(facts[0:len(facts)-1])
					fact = fact[0]
					#print fact
					#print 'Found some facts for tweet', i.idnum
					i.reply = '@' + i.user.encode('ascii','replace') + ' ' + price.encode('utf8') + ' ' + fact.encode('raw-unicode-escape')
				else:
					i.reply = '@' + i.user.encode('ascii','replace') + ' Sorry, I don\'t understand. I only understand postcodes.'
					#print 'No fact found for tweet: ', i.idnum
					logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' No fact found for tweet: ' + str(i.idnum) + ' ' + str(i.text) + '\n')
			#show replies
			#for i in tweets:
			#	print i.text, i.idnum, i.user, i.reply

			#post updates and update database
			for i in tweets:
				if i.reply != None:
					api.PostUpdate(i.reply, i.idnum)
					#print 'Tweeted: ',i.reply
					logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' Tweeted: ' + str(i.reply) + '\n')
					insertTweet(i.idnum)
				else:
					#print 'No reply created for tweet id: ', i.idnum
					logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' No reply created for tweet id: ' + str(i.idnum) + '\n')

		   	ratelimits = api.GetRateLimitStatus(u'statuses')

			remaininggetmentions = ratelimits[u'resources'][u'statuses'][u'/statuses/mentions_timeline'][u'remaining']

			#print 'I have %d remaining get mentions left.' % (remaininggetmentions)

		#if twitter says we have already tweeted that, record it and update the database to prevent it happening again
		except twitter.error.TwitterError, e:
			if int(e[0][0][u'code']) == 187:
				#print 'Duplicate Error!'
				logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' Duplicate Error\n')
				#fetch the tweets we've made
				mytweets = api.GetUserTimeline(2813607432)
				logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' Checking Tweets\n')
				#create a list of instances of tweet to store tweets
				alreadytweeted = [tweet() for i in mytweets]
				#pull data from mytweets and populate the alreadytweeted list
				for j,i in enumerate(alreadytweeted):
					i.idnum = mytweets[j].in_reply_to_status_id
					#print i.idnum
				#remove those already in the database
				for i in alreadytweeted[:]:
					if checkTweets(i.idnum):
						alreadytweeted.remove(i)
				#insert the missing tweets				
				for i in alreadytweeted:
					logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' Tweet ' + str(i.idnum) + 'is duplicate\n')
					insertTweet(i.idnum)
				#insert remaining tweets into database twitter won't let you tweet the warning twice!
				for i in tweets:
					logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' Tweet ' + str(i.idnum) + 'is duplicate, probably tweeted this user before\n')
					insertTweet(i.idnum)
				time.sleep(62)
				pass
			if int(e[0][0][u'code']) == 88:
				logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' Limit reached, sleep for 15mins\n')
				time.sleep(901)
			else:
				raise

		#except:
		#	logger(strftime("%Y-%m-%d %H:%M:%S",gmtime()) + ' Error: ' + str(sys.exc_info()[0]) + '\n')
		#	raise

		finally:
			#go to sleep for 62 seconds
			time.sleep(62)

		#	print 'Timeout Error: going to sleep for 900 seconds'
		#	time.sleep(900)

main()
