from django.conf import settings #then do settings.theVariableYouWantToAccess
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from .models import User, Tweet
from twython import Twython, TwythonError
from datetime import datetime, timezone
from gensim.models import Word2Vec
from nltk.cluster import KMeansClusterer
from sklearn import cluster, metrics
from tweet_generator import tweet_generator
import gensim
import nltk
import pytz
import os


appname = 'genatweetor'
NUMBER_OF_CLUSTERS = 10

def is_loggedin(view):
    def isloggedinView(request):
        #Check to see if the user's username is in the request
        if 'username' in request.session:
            username = request.session['username']
            try:
                userAccount = User.objects.get(username=username)
            except User.DoesNotExist:
                raise Http404('That username does not exist! Please Try again!')
            return view(request, userAccount)
        else:
            return render(request, 'genatweetor/login.html')
    return isloggedinView

#LOGIN VIEW
def index(request):
    response ={
        'responseMessage' : "Welcome To genatweetor! Login to Continue!"
    }
    return render(request, 'genatweetor/login.html', response)

def login(request):
    if not ('form-username' in request.POST and 'form-password' in request.POST):
        response = {
            'responseMessage' : "Please enter your username or password correctly!"
        }
        return(request, 'genatweetor/login.html', response)
    else:
        username = request.POST.get('form-username')
        password = request.POST.get('form-password')
        try:
            user = User.objects.get(username=username)
        except(User.DoesNotExist):
            response = {
                'responseMessage': "User does not exist, Please try a different Username"
            }
            return render(request, 'genatweetor/login.html', response)
        if(user.check_password(password)):
            request.session['username'] = username
            request.session['password'] = password
            # #################################################
            twitter = Twython(app_key=settings.APP_KEY , app_secret=settings.APP_SECRET)
            #callback url
            auth = twitter.get_authentication_tokens(callback_url='http://127.0.0.1:8000/dashboard')
               #Change to https://genatweetor.herokuapp.com/dashboard after testing is done
            #save oauth tokens into a session variable (a temporary method of storing the oauth variables)
            request.session['oauth_token'] = auth['oauth_token']
            request.session['oauth_token_secret'] = auth['oauth_token_secret']
            #Redirect the user to the url obtained by twitter
            redirect_url = auth['auth_url']

            #redirect to twitter login
            return redirect(redirect_url)
            # #################################################
            return dashboard(request)
        else:
            response = {
                'responseMessage':"Incorrect Username or Password. Please Try again!"
            }
            return render(request, 'genatweetor/login.html', response)

def register(request):
    firstName = request.POST.get('firstName')
    lastName = request.POST.get('lastName')
    email = request.POST.get('email')
    dateOfBirth = request.POST.get('dateofbirth')
    username = request.POST.get('username')
    password = request.POST.get('password')
    if not 'firstName' in request.POST and not 'lastName' in request.POST and not 'username' in request.POST and not 'email' in request.POST and not 'dob' in request.POST and not 'password' in request.POST:
        response = {
        'responseMessage' : "Please fill in all fields to Register!"
        }
        return render(request, 'genatweetor/register.html', response)

    else:
        if username == '' or password == '':
            response = {
                'responseMessage' : "Please enter a username and password!"
            }
            return render(request, 'genatweetor/register.html', response)
        user = User(username=username, first_name=firstName, last_name=lastName, email=email, dob=dateOfBirth)

        user.set_password(password)
        try:
            user.save()
            # If any credentials are already saved to the database
        except IntegrityError as e:
            response = {
                'responseMessage' : "Username or E-mail is already Taken, Please enter something different"
                }
            return render(request, 'genatweetor/register.html', response)
        response = {
            'responseMessage' : "You have been successfully registered! You can now Login!"
        }
        return render(request, 'genatweetor/login.html', response)
    response = {
        'responseMessage' : "You have been successfully registered! You can now Login!"
    }
    return render(request, 'genatweetor/login.html', response)

@is_loggedin
def dashboard(request, user):
     # if user denied authorization
    if 'denied' in request.session:
        return HttpResponse("USER DENIED")
    twitter = Twython(settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
    credentials = twitter.verify_credentials()
    userID = str(user.id)
    location = 'temp/word2vecModels/word2vecModel-User'
    file = location + userID + ".txt"
    exists = os.path.isfile(file)
    if exists:
        w2vModel = gensim.models.Word2Vec.load(file)
        w2vModelVocab = w2vModel[w2vModel.wv.vocab]
        clusterer = KMeansClusterer(NUMBER_OF_CLUSTERS, distance=nltk.cluster.cosine_distance, repeats=30)
        clusters = clusterer.cluster(w2vModelVocab, assign_clusters=True)
        word_list = list(w2vModel.wv.vocab)
        kmeans = cluster.KMeans(n_clusters = NUMBER_OF_CLUSTERS)
        kmeans.fit(w2vModelVocab)
        kMeans_labels = kmeans.labels_
        KMeansScore = kmeans.score(w2vModelVocab)
        silScore = metrics.silhouette_score(w2vModelVocab, kMeans_labels, metric='euclidean')
        sum = 0
        count = 0
        retweetSum = 0
        favouriteSum = 0
        tweetObjects = Tweet.objects.filter(userTweeted_id=user.id)
        for tweet in tweetObjects:
            count = count + 1
            sum = sum + tweet.calculateTweetScore()
            retweetSum = retweetSum + tweet.tweetRetweets
            favouriteSum = favouriteSum + tweet.tweetFavourites
        AverageRetweetScore = (retweetSum * 0.567)/count
        AverageFavouriteScore = (favouriteSum * 0.486)/count
        engagementScore = sum / count
    else:
        AverageRetweetScore = 0.0
        AverageFavouriteScore = 0.0
        engagementScore = 0.0
        KMeansScore = 0
        silScore = 0
    response = {
        'name' : user.first_name + " " + user.last_name,
        'twitterName': credentials['name'],
        'user': user.username,
        'screen_name': credentials['screen_name'],
        'email': user.email,
        'dob': user.dob,
        'age': user.getUserAge(),
        'tweetCount' : user.getTweetCount(),
        'followerCount': user.getFollowerCount(),
        'accountDescription' : user.accountDescription,
        'responseMessage' : "Welcome to Genatweetor",
        'retweetScore':AverageRetweetScore,
        'favouriteScore':AverageFavouriteScore,
        'engagementScore':engagementScore,
        'kmeans':KMeansScore,
        'silhouetteScore':silScore
    }
    return render(request, 'genatweetor/dashboard.html', response)

@is_loggedin
def profile(request, user):
    response = {
        'username': user.username,
        'first_name':user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'dob': user.dob
    }
    return render(request, 'genatweetor/profile.html', response)
#Helper method view Used for Ajax Calls
@is_loggedin
def getTwitterProfile(request, user):
    profileAttributes = []
    twitter = Twython(settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
    credentials = twitter.verify_credentials()
    screenName = credentials['screen_name']

    userAttributes = twitter.show_user(screen_name=screenName)
    profileImage = userAttributes['profile_image_url_https']
    profileDescription = userAttributes['description']
    followerCount = userAttributes['followers_count']
    tweetCount = userAttributes['statuses_count']
    name = userAttributes['name']
    twitterProfile = {
        'screen_name':screenName,
        'twitterName': name,
        'profileImageLink':profileImage,
        'accountDescription':profileDescription,
        'followerCount':followerCount,
        'tweetCount':tweetCount
    }
    profileAttributes.append(twitterProfile)
    return JsonResponse(profileAttributes, safe=False)
#Helper method view Used for Ajax Calls
@is_loggedin
def getDjangoProfile(request, user):
    profileAttributes = []
    twitter = Twython(settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
    credentials = twitter.verify_credentials()
    screenName = credentials['screen_name']
    userAttributes = twitter.show_user(screen_name=screenName)
    user.save()
    query = User.objects.filter(id=user.id).values('first_name', 'last_name', 'username', 'email', 'numberOfGeneratedTweets')
    return JsonResponse(list(query), safe=False)

@is_loggedin
def editUserProfile(request,user):
    if not 'first_name' in request.POST and 'last_name' in request.POST and 'email' in request.POST:
        response = {
            "Please fill in all fields before submitting!"
        }
        return JsonResponse(list(response),safe=False)
    else:
        if request.POST is not None:
            if 'first_name' in request.POST and request.POST is not None:
                user.first_name = request.POST['first_name']

            if 'last_name' in request.POST and request.POST is not None:
                user.last_name = request.POST['last_name']

            if 'email' in request.POST and request.POST is not None:
                user.email = request.POST['email']
            try:
                user.save()
            except IntegrityError:
                response = {
                    "Something you entered already exists! please choose something different!"
                }
                return JsonResponse(list(response), safe=False)
        else:
            response = {
                "Oops! Something went Wrong! Please Try again Later!"
            }
            return JsonResponse(list(response), safe=False)

        response = {
            "Changes Successfully saved!"
        }
        return JsonResponse(response, safe=False)

@is_loggedin
def tweetsArchive(request, user):
    return render(request, 'genatweetor/tweetsArchive.html')

@is_loggedin
def getTweets(request,user):
    twitter = Twython(settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
    credentials = twitter.verify_credentials()
    tweetObjects = Tweet.objects.filter(tweetedBy=credentials['screen_name'])
    if tweetObjects:
        tweets = []
        for tweet in tweetObjects:
            text = tweet.getTweetText()
            date = tweet.getDateTweeted()
            user = tweet.getUserTweeted()
            retweetCount = tweet.getRetweetCount()
            favouriteCount = tweet.getFavouriteCount()

            tweetAttributes = {
                'tweetID':tweet.tweetID,
                'tweetText':text,
                'tweetDate':date,
                'tweetedBy':user,
                'tweetFavourites': favouriteCount,
                'tweetRetweets': retweetCount
            }
            tweets.append(tweetAttributes)
            #call score tweet
        return JsonResponse(tweets, safe=False)
    else:
        response = []
        response.append(list(tweetObjects))
        return JsonResponse(response, safe=False)

def trainModel(user):
    clean_tweets = []
    userID = str(user.id)
    location = 'temp/word2vecModels/word2vecModel-User'
    file = location + userID + ".txt"
    exists = os.path.isfile(file)
    if Tweet.objects.filter(userTweeted_id=user.id, usedInTraining=False).exists():
        if os.path.isfile(file):
            w2vModel = gensim.models.Word2Vec.load(file)
            tweetObjects = Tweet.objects.filter(userTweeted_id=user.id, usedInTraining=False)
            for tweet in tweetObjects:
                if tweet.usedInTraining==False:
                    clean_tweets.append(tweet.cleanTweetText())
                    tweet.usedInTraining = True
                    tweet.save()
                else:
                    continue
            w2vModel.train(clean_tweets, total_examples=w2vModel.corpus_count, epochs=w2vModel.iter)
            w2vModel.save(file)
        else:
            tweetObjects = Tweet.objects.filter(userTweeted_id=user.id, usedInTraining=False)
            for tweet in tweetObjects:
                if tweet.usedInTraining==False:
                    clean_tweets.append(tweet.cleanTweetText())
                    tweet.usedInTraining = True
                    tweet.save()
                else:
                    continue
            model = Word2Vec(clean_tweets, size=150, window=10, min_count=1,workers=10,iter=10)
            model.save(file)
    return

@is_loggedin
def updateTimeline(request,user):
        tweetObjects = []
        tweets = []
        if not 'count' in request.POST:
            response = {
                'responseMessage':"Please enter a value!"
            }
            return response
        else:
            count = int(request.POST['count'])
            twitter = Twython(settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
            credentials = twitter.verify_credentials()
            SCREEN_NAME = credentials['screen_name']
            try:
                user_timeline = twitter.get_user_timeline(screen_name=SCREEN_NAME, exclude_replies=True, include_rts=True, count=count)
            except TwythonError as e:
                raise Http404(e)
            for tweet in user_timeline:
                id = int(tweet['id_str'])
                favouritecounter = tweet['favorite_count']
                retweetcounter = tweet['retweet_count']
                if Tweet.objects.filter(tweetID=id).exists():
                    continue
                text = tweet['text']
                timezone = pytz.timezone('UTC')
                tweetDate = datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
                date = timezone.localize(tweetDate)
                userTweet = Tweet(userTweeted=user,tweetID=id, tweetedBy=SCREEN_NAME, tweetText=text, tweetDate=date, tweetFavourites=favouritecounter, tweetRetweets=retweetcounter)
                tweetObjects.append(userTweet)
                try:
                    print(userTweet)
                    userTweet.save()
                except IntegrityError as e:
                    print("IntegrityError")
                    print(e)
                    continue
            for tweet in tweetObjects:
                text = tweet.getTweetText()
                date = tweet.getDateTweeted()
                userTweeted = tweet.getUserTweeted()
                retweetCount = tweet.getRetweetCount()
                favouriteCount = tweet.getFavouriteCount()

                tweetAttributes = {
                    'tweetText':text,
                    'tweetDate':date,
                    'tweetedBy':userTweeted,
                    'tweetFavourites': favouriteCount,
                    'tweetRetweets': retweetCount
                }
                tweets.append(tweetAttributes)
            trainModel(user)
            return JsonResponse(tweets, safe=False)

def deleteTweet(request, tweetID):
    #get the tweet text and search for it in the database
    #delete the tweet object
    if request.method == "DELETE":
        if Tweet.objects.filter(tweetID=tweetID).exists():
            delTweet = Tweet.objects.filter(tweetID=tweetID)
            delTweet.delete()
            responseMessage = {
                "Deleted!"
            }
            return JsonResponse(list(responseMessage), safe=False)
        else:
            responseMessage = {
                "OOPS! Something went Wrong! The tweet you tried to delete does not exist!"
            }
            return JsonResponse(list(responseMessage), safe=False)
    else:
        responseMessage = {
            "OOPS! Something went Wrong!"
        }
        return JsonResponse(list(responseMessage), safe=False)

@is_loggedin
def generateTweet(request,user):
    return render(request, 'genatweetor/generateTweet.html')

@is_loggedin
def generateTweets(request,user):
    if 'count' in request.POST:
        count = request.POST['count']
        generatedTweets = []
        twitter = Twython(settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
        credentials = twitter.verify_credentials()
        twitter_id = credentials['id']
        generator = tweet_generator.PersonTweeter(str(twitter_id), settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
        for i in range(int(count)):
            generated_tweet = generator.generate_random_tweet()
            generatedTweets.append(generated_tweet)
        return JsonResponse(list(generatedTweets), safe=False)


def postTweet(request):
    tweetText = request.POST['tweetText']
    twitter = Twython(settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
    twitter.update_status(status=tweetText)
    response = {"Successful!"}
    return JsonResponse(list(response), safe=False)

@is_loggedin
def logout(request,user):
    request.session.flush()
    return render(request, 'genatweetor/login.html', {'responseMessage': "Successfully Signed-out! Thank you for using genatweetor!!"})
