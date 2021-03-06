
#===============useful below=========
#http://www.mikaelbrunila.fi/2017/03/27/scraping-extracting-mapping-geodata-twitter/
#https://github.com/fbkarsdorp/twitter-workshop
#https://stackoverflow.com/questions/17633378/how-can-we-get-tweets-from-specific-country
#http://www.dealingdata.net/2016/07/23/PoGo-Series-Tweepy/
#http://docs.tweepy.org/en/v3.5.0/

#===================not useful==================
#https://blog.csdn.net/hectorli36/article/details/76590203
#https://blog.csdn.net/Andy_Shan/article/details/51878803
#https://blog.csdn.net/p_function/article/details/77531707
#http://python.jobbole.com/87833/
#distribution 


#twitter time

import tweepy
from tweepy import Stream
from tweepy import StreamListener 
from tweepy import OAuthHandler
import json
import numpy as np
consumer_key = "Lj4Uykjhmcpi7bsGeZXMxPISk"
consumer_secret = "6aZ7T4Au0Tv4M2C5p7gCQVapTNy8rcF6kGlAwilculNqcP8fuH"
access_token = "3074259759-Llu1Uz6SGywiT9P9B7AdkO85t75VMYNwQmtB620"
access_secret = "nbjVpbWBAChf8RSXVLkMv9PgZPs3C6Cbi3QTYJDtbM5wZ"

TWEET_NUM=5
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

#search by country
places = api.geo_search(query="Australia", granularity="country")
#search by city
places = api.geo_search(query="Melbourne", granularity="city")


#print(places)

bb=places[0].bounding_box.coordinates[0]
bb=np.array(bb)
#use a rough bounding box (rectangle) instead of a rigid polygon
bounding_box=[np.min(bb[:,0]),np.min(bb[:,1]),np.max(bb[:,0]),np.max(bb[:,1])]
print("bounding box is",bounding_box)
place_id = places[0].id

print("============================")

@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status
 
# Status() is the data model for a tweet
tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse
cnt=0
class MyListener(StreamListener):
    def __init__(self, api=None):
       super(self.__class__, self).__init__()
       self.num_tweets = 0

    def on_data(self, data):
        try:
            #add database operation here....
            print(data)
            self.num_tweets+=1
            with open('data.txt','a',encoding='utf-8') as f:
                f.write(data)


        except BaseException as e:
            print("Error on_data: %s" % str(e))

        if self.num_tweets>=TWEET_NUM:
            return False
            
        return True
 
    def on_error(self, status):
        print(status)

        return True

    #https://github.com/tweepy/tweepy/issues/935
    #returning False in on_error disconnects the stream
    #prevent the exponentially increased time of rate limiting  
    def test_rate_limit(api, wait=True, buffer=.1):
            """
            Tests whether the rate limit of the last request has been reached.
            :param api: The `tweepy` api instance.
            :param wait: A flag indicating whether to wait for the rate limit reset
                     if the rate limit has been reached.
            :param buffer: A buffer time in seconds that is added on to the waiting
                       time as an extra safety margin.
            :return: True if it is ok to proceed with the next request. False otherwise.
            """
            #Get the number of remaining requests
            remaining = int(api.last_response.getheader('x-rate-limit-remaining'))
            #Check if we have reached the limit
            if remaining == 0:
                limit = int(api.last_response.getheader('x-rate-limit-limit'))
                reset = int(api.last_response.getheader('x-rate-limit-reset'))
                #Parse the UTC time
                reset = datetime.fromtimestamp(reset)
                #Let the user know we have reached the rate limit
                print("0 of {} requests remaining until {}.".format(limit, reset))

            if wait:
                #Determine the delay and sleep
                delay = (reset - datetime.now()).total_seconds() + buffer
                print("Sleeping for {}s...".format(delay))
                sleep(delay)
                #We have waited for the rate limit reset. OK to proceed.
                return True
            else:
                #We have reached the rate limit. The user needs to handle the rate limit manually.
                return False 

            #We have not reached the rate limit
            return True

twitter_stream = Stream(auth, MyListener())

print("stream connected!")


#its said that filter can search data in 7 days, while api.search can only search data in a much shorter time
twitter_stream.filter(locations=bounding_box)  #track=['sleep']   #add hashtag

# tweets = api.search(q="place:%s" % place_id,count=1000)
# for tweet in tweets:
#     print( tweet.text + " | " + tweet.place.name if tweet.place else "Undefined place")



import json
import collections
with open("data.txt","r",encoding="utf-8") as f:
    linenum=len([ "" for line in f])

m=collections.OrderedDict()
# m=[]
i=0
with open("data2.json","w",encoding="utf-8") as f2:
    f2.write("{\"total_rows\":%d,\"offset\":0,\"rows\":[\n"%linenum)
    with open("data.txt","r",encoding="utf-8") as f:
        for line in f:
            i+=1
            lj=json.loads(line)
            x=json.dumps(lj)
            f2.write(x)
            if i < linenum:
                f2.write(",\n")
            else:
                f2.write("\n")
        

    f2.write("]}\n")
