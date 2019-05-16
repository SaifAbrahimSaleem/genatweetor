from django.db import models # Import models from django's db module
from django.contrib.auth.models import User # From django's authentication models, import the User object
from datetime import date # import date from the datetime module. This will be used later on when calculating a user's age
from nltk.corpus import stopwords # import all known stopwords from nltk's corpus (collection of words) module
#from nltk.stem import PorterStemmer # import the PorterStemmer object from nltk's stem module. This will be used later on when associating similar words to a generalised word
from nltk.tokenize import TweetTokenizer # import the TweetTokenizer object from nltk's tokenize module. This will be used later on when turning a string sentence into a set of words for later processing
import string # Import the string module. This will be used later on in the program for when tweets are cleaned.
import re # Import the regular expressions module. This will be used for later on in the program when tweets are cleaned

tweet_tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True) # Create a new Tokenizer object. This will take a string sentence, convert all characters to lowercase, remove twitter handles and reduce the length of the tweet (if necessary) and return a set of individual words within the sentence (tokens)
list_of_stopwords = set(stopwords.words("english")) # list of common english words provided by nltk
#word_stemmer = PorterStemmer() # Create a new word stemmer object. This will allow for the generalisation of common words with the same meaning

class User(User): # class User extends django.contrib.auth.model's current User model
    dob = models.DateTimeField('Date of Birth') # Store the user's date of birth
    tweetCount = models.IntegerField(blank=True, default=0) # Store the amount of tweets associated with the user's twitter account
    followerCount = models.IntegerField(blank=True, default=0) # Store the amount of followers associated with the user's twitter account
    accountDescription = models.CharField(max_length=300, blank=True, default='Hello World! I am using Genatweetor!') # store the account description associated with the user
    numberOfGeneratedTweets = models.IntegerField(blank=True, default = 0) # Store the number of generated tweets associated with the user
    engagementScore = models.DecimalField(default = 0.00, blank=True, max_digits = 8, decimal_places=2)
    ########## USER MODEL ALREADY HAS USERNAME, PASSWORD AND EMAIL ##########

    #return username/name string representation associated with the user object
    def __str__(self): # return a string representation of the user object
        return self.username # return the username associated with the genatweetor account

    def getUserAge(self): # calculate the age of the user for representation on profile
        currentDate = date.today() #get todays date
        ageYear = int(currentDate.year) - int(self.dob.year) # calculate the age in terms of the year from the difference between the current year and birth year
        if currentDate.month<self.dob.month: # if the difference between current month and the birth month is high
            ageYear -=1 # Take away a year
        elif currentDate.day<self.dob.day: # if the difference between the current month and the birth month is high
            ageYear -= 1 # also take away a year
        return ageYear # return the user's age

    def getFollowerCount(self):
        return self.followerCount # return the follower account associated with the user

    def getTweetCount(self):
        return self.tweetCount # return the tweet count associated with the user

    def getAccountDescription(self):
        return self.accountDescription # return the account description associated with the user's twitter account



class Tweet(models.Model): # Class tweet extends the model class
    userTweeted = models.ForeignKey(User, on_delete=models.CASCADE) # store the user associated with the tweet, when deleted cascade the entry
    # fields can be blank as the user will not have a tweet associated with their account until they stream the tweet from twitter
    tweetID = models.IntegerField(primary_key=True, blank=True) # Store the tweet ID in a character field. This could potentially be the primary key
    tweetedBy = models.CharField(max_length=100, blank=True) # Store the screen name of the user tweeted in a character field. This may have use in future if time is permitting
    tweetText = models.CharField(max_length=250, blank=True) # Store the text associated with the tweet in a character field
    tweetDate = models.DateTimeField('Date Tweeted') # Store the date associated with the tweet in a date time field
    tweetFavourites = models.IntegerField(default=0, blank=True) # Store the number of favourites associated with the tweet in an integer field
    tweetRetweets = models.IntegerField(default=0, blank=True) # store the number of retweets associated with the tweet in an integer field
    tweetScore = models.DecimalField(default=0.0, decimal_places=2, max_digits=4, blank=True) #store the tweet's score in a decimal field
    isGenerated = models.BooleanField(default=False, blank=True)
    usedInTraining = models.BooleanField(default=False, blank=True)

    def __str__(self): # return a string representation of the tweet
        return "ID: " + str(self.tweetID) + "    " +"   Tweet Text:   " + self.tweetText + "    " + " Tweet Date: "+ str(self.tweetDate) # return a concatenation of the string representation of the ID, tweet text and the date associated with the tweet

    def getUserTweeted(self):
        return self.tweetedBy # return the twitter handle associated with the tweet

    def getTweetText(self):
        return self.tweetText # return the text associated with the tweet

    def getDateTweeted(self):
        return self.tweetDate # return the date associated with the tweet

    def getRetweetCount(self):
        return self.tweetRetweets # return the number of retweets associated with the tweet

    def getFavouriteCount(self):
        return self.tweetFavourites # return the number of favourites associated with the tweet

    def calculateTweetScore(self):
        return ((self.tweetRetweets * 0.567) + (self.tweetFavourites * 0.486))/2

    # REGULAR EXPRESSIONS USED:
    # \S - represents non-whitespace characters
    # ^ - matches the start of a string
    # + - denotes that the regular expression contained before it can be recurring

    # Tweet preprocessing used is based off of the following citation:
    # @Citation = {
    #   author = 	"Max Woolf",
    #   title = 	"Tweet Generator",
    #   Code = (Method) process_tweet_text - preprocessing tweets in preparation for later use. [Regular expressions were used]
    #   year = 	"2018",
    #   License = "MIT License",
    #   location = 	"San Francisco, United States",
    #   url = 	"https://github.com/minimaxir/tweet-generator"
    #   }


    def cleanTweetText(self):
        cleaned_tweet = [] # tokens of the cleaned tweet
        tweet_text_RTs = re.sub('^RT[\s]+','', self.tweetText) #remove RT from the start of the tweet if applicable
        tweet_text_hyperlink = re.sub(r'http\S+', '' , tweet_text_RTs) #remove hyperlinks if applicable
        tweet_text_hashtag = re.sub(r'#','',tweet_text_hyperlink) # replace hashtags and replace them with HASHTAG
        tweet_text = re.sub(r'&lt;', '<', tweet_text_hashtag) # remove commonly used HTML elements
        tweet_text = re.sub(r'&gt;', '>', tweet_text) # remove commonly used HTML elements
        tweet_text = re.sub(r'&amp;', '&', tweet_text) # remove commonly used HTML elements
        tokens = tweet_tokenizer.tokenize(tweet_text) # from the tweet texts, return a substring containing all of the words
        for word in tokens: # for each word that is part of the tokens
            if(word not in list_of_stopwords and word not in string.punctuation and word != '.' and word !='..' and word !='....'):
                #stem_word = word_stemmer.stem(word) # stem similar words together into a generalised word
                cleaned_tweet.append(word) # append the result to the cleaned tweet
        return cleaned_tweet # return the cleaned tweet

    def cleanForGeneration(self):
        tweet_text_RTs = re.sub('^RT[\s]+','', self.tweetText) #remove RT from the start of the tweet if applicable
        tweet_text_hyperlinks = re.sub(r'http\S+', '', tweet_text_RTs)   # Remove URLs
        tweet_text_usernames = re.sub(r'@[a-zA-Z0-9_]+', '', tweet_text_hyperlinks)  # Remove user mentions from tweet if applicble
        tweet_text_usernames = tweet_text_usernames.strip(" ")   # Remove whitespace resulting from above
        cleaned_tweet = re.sub(r' +', ' ', tweet_text_usernames)   # Remove redundant spaces
        cleaned_tweet = re.sub(r'&lt;', '<', cleaned_tweet) # remove commonly used HTML elements
        cleaned_tweet = re.sub(r'&gt;', '>', cleaned_tweet) # remove commonly used HTML elements
        cleaned_tweet = re.sub(r'&amp;', '&', cleaned_tweet) # remove commonly used HTML elements
        return cleaned_tweet # return the cleaned tweet
