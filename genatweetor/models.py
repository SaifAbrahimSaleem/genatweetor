from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.http import JsonResponse

# Create your models here.
#   MODELS REQUIRED (i think)
#       USER
#       TWEET
#       RECOMMENDED TWEETS
#       TIMELINE
class User(User):
    dob = models.DateTimeField('Date of Birth')
    twitterName = models.CharField(max_length=100, blank=True)
    #profileImage = models.ImageField(upload_to='profileImages', blank=True) #profile_image_url or profile_image_url_https
    tweetCount = models.IntegerField(blank=True, default=0) #statuses_count
    followerCount = models.IntegerField(blank=True, default=0) #followers_count
    accountDescription = models.CharField(max_length=300, blank=True, default='Hello World! I am using Genatweetor!')
    numberOfGeneratedTweets = models.IntegerField(blank=True, default = 0)
    ########## USER MODEL ALREADY HAS USERNAME, PASSWORD AND EMAIL ##########
    #return username/name
    def __str__(self):
        return self.username

    def getUserAge(self):
        currentDate = date.today()
        ageYear = int(currentDate.year) - int(self.dob.year)
        if currentDate.month<self.dob.month:
            ageYear -=1
        elif currentDate.day<self.dob.day:
            ageYear -= 1
        return ageYear

    def getFollowerCount(self):
        return self.followerCount

    def getTweetCount(self):
        return self.tweetCount

    def getAccountDescription(self):
        return self.accountDescription
    #return age
    #return tweetcount
    #return follower count

class Tweet(models.Model):
    userTweeted = models.ForeignKey(User, on_delete=models.CASCADE)
    tweetID = models.CharField(max_length=200, blank=True)
    tweetedBy = models.CharField(max_length=100, blank=True)
    tweetText = models.CharField(max_length=250, blank=True)
    tweetDate = models.DateTimeField('Date Tweeted')
    #tweetedBy could be a thing
    #ADD ENGAGEMENT PARTS LATER WHEN MEASURING ENGAGEMENT:


    def __str__(self):
        return "ID: " + str(self.id) + "    " +"   Tweet Text:   " + self.tweetText + "    " + " Tweet Date: "+ str(self.tweetDate)

    def getUserTweeted(self):
        return self.tweetedBy

    def getTweetText(self):
        return self.tweetText

    def getDateTweeted(self):
        return self.tweetDate

#class GeneratedTweet(models.Model):
