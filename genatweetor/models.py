from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
#   MODELS REQUIRED (i think)
#       USER
#       TWEET
#       RECOMMENDED TWEETS
#       TIMELINE
class User(User):
    name = models.CharField(max_length=100, blank=True)
    dob = models.DateTimeField('Date of Birth')
    profileImage = models.ImageField(upload_to='profileImages') #profile_image_url or profile_image_url_https
    tweetCount = models.IntegerField() #statuses_count
    followerCount = models.IntegerField() #followers_count
    ########## USER MODEL ALREADY HAS USERNAME, PASSWORD AND EMAIL ##########
    #return username/name
    def __str__(self):
        return self.username

    def getUserAge(self):
        today = date.today
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def getFollowrtCount(self):
        return self.followerCount

    def getTweetCount(self):
        return self.tweetCount
    #return age
    #return tweetcount
    #return follower count

class Tweet(models.Model):
    tweetedBy = models.CharField(max_length=100, blank=True)
    tweetText = models.CharField(max_length=250, blank=True)
    tweetDate = models.DateTimeField('Date Tweeted')
    #tweetedBy could be a thing
    #ADD ENGAGEMENT PARTS LATER WHEN MEASURING ENGAGEMENT:


    def __str__(self):
        return self.tweetText

    def getUserTweeted(self):
        return self.tweetedBy

    def getDateTweeted(self):
        return self.tweetDate
