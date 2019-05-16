from django.conf import settings # import the settings for twitter keys
from django.shortcuts import render, redirect # import the render and redirect methods from the django shortcuts package. These will be used to direct the flow of the program
from django.http import HttpResponse, JsonResponse, Http404 # import response methods
from django.db import IntegrityError # import an Integrity exception for when the data integrity of the database has been breached.
from .models import User, Tweet # import the User and Tweet models in order to create, delete and manipulate modelled datastructures
from twython import Twython, TwythonError #Import Twython, the module which is used to aid in tritter communications
from datetime import datetime, timezone #import datetime and datetimezone from the datetime module. These will be used later on when converting from Twitter time to UTC time
from gensim.models import Word2Vec # Import the Word2Vec model from gensims model package
from nltk.cluster import KMeansClusterer # import the KMeansClusterer model from nltk's cluster package
from sklearn import cluster, metrics # import the cluster and metrics models from SKlearn for later use when calculating KMeans
from tweet_generator import tweet_generator # Import the Tweet Generator Model from the Tweet Generator package
import gensim
import nltk
import pytz
import os


appname = 'genatweetor' # declare the application name. This allows for traversal through the application directories
NUMBER_OF_CLUSTERS = 10 # set the number of clusers to 10. This number was simply chosen and thus holds no significance
# in the reasons for as to why it was chosen
# create a decorator which will keep track of the user's state each time a view is executed. in this case the decorator method is checking to see if the user is logged in
# This particular decorator was inspired by the Web Programming group project
def is_loggedin(view): # take the view as an argument
    def isloggedinView(request):
        #Check to see if the user's username is in the request
        if 'username' in request.session: # if the username is in the session variable
            username = request.session['username'] # create a new variable called username and give it the value of the username session variable
            try: # attempt to search for the user to return it later on in the program
                userAccount = User.objects.get(username=username) # if the user exists, store it as a variable
            except User.DoesNotExist: # otherwise if the user does not exist, throw an error
                raise Http404('That username does not exist! Please Try again!') # raise a http 404 response to the user saying that the user does not exist
            return view(request, userAccount) # otherwise, return the view which is being evaluated, passing the request and the account that has been found
        else: # otherwise if the username is not contained in the session variable
            return render(request, 'genatweetor/login.html') # return the login template with the request.
    return isloggedinView # return to the view

#LOGIN VIEW
def index(request):
    response ={
        'response' : "Welcome To genatweetor! Login to Continue!"
    }
    return render(request, 'genatweetor/login.html', response)

def login(request):
    if not ('form-username' in request.POST and 'form-password' in request.POST):
        response = {
            'response' : "Please enter your username or password correctly!"
        }
        return(request, 'genatweetor/login.html', response)
    else:
        username = request.POST.get('form-username')
        password = request.POST.get('form-password')
        try:
            user = User.objects.get(username=username)
        except(User.DoesNotExist):
            response = {
                'response': "User does not exist, Please try a different Username"
            }
            return render(request, 'genatweetor/login.html', response)
        if(user.check_password(password)):
            request.session['username'] = username
            request.session['password'] = password
            # #################################################
            twitter = Twython(app_key=settings.APP_KEY , app_secret=settings.APP_SECRET)
            #callback url
            auth = twitter.get_authentication_tokens(callback_url='https://genatweetor.herokuapp.com/dashboard')
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
                'response':"Incorrect Username or Password. Please Try again!"
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
        'response' : "Please fill in all fields to Register!"
        }
        return render(request, 'genatweetor/register.html', response)

    else:
        if username == '' or password == '':
            response = {
                'response' : "Please enter a username and password!"
            }
            return render(request, 'genatweetor/register.html', response)
        user = User(username=username, first_name=firstName, last_name=lastName, email=email, dob=dateOfBirth)

        user.set_password(password)
        try:
            user.save()
            # If any credentials are already saved to the database
        except IntegrityError as e:
            response = {
                'response' : "Username or E-mail is already Taken, Please enter something different"
                }
            return render(request, 'genatweetor/register.html', response)
        response = {
            'response' : "You have been successfully registered! You can now Login!"
        }
        return render(request, 'genatweetor/login.html', response)
    response = {
        'response' : "You have been successfully registered! You can now Login!"
    }
    return render(request, 'genatweetor/login.html', response)

@is_loggedin
def dashboard(request, user):
     # if user denied authorization
    if 'denied' in request.session:
        return HttpResponse("USER DENIED")
    if 'oauth_verifier' in request.GET:
        oAuthVerifier = request.GET['oauth_verifier']
        twitter = Twython(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, oauth_token=request.session['oauth_token'], oauth_token_secret=request.session['oauth_token_secret'])
        tokens = twitter.get_authorized_tokens(oAuthVerifier)
        request.session['oauth_token']= tokens['oauth_token']
        request.session['oauth_token_secret'] = tokens['oauth_token_secret']
    newTwitter = Twython(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, oauth_token=request.session['oauth_token'], oauth_token_secret=request.session['oauth_token_secret'])
    user_credentials = newTwitter.verify_credentials()
    userID = str(user.id)
    location = 'temp/word2vecModels/word2vecModel-User'
    file = location + userID + ".txt"
    exists = os.path.isfile(file)
    if exists:
        try:
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
        except ZeroDivisionError:
            pass
    else:
        AverageRetweetScore = 0.0
        AverageFavouriteScore = 0.0
        engagementScore = 0.0
        KMeansScore = 0
        silScore = 0
    response = {
        'name' : user.first_name + " " + user.last_name,
        'twitterName': user_credentials['name'],
        'user': user.username,
        'screen_name': user_credentials['screen_name'],
        'email': user.email,
        'dob': user.dob,
        'age': user.getUserAge(),
        'tweetCount' : user.getTweetCount(),
        'followerCount': user.getFollowerCount(),
        'accountDescription' : user.accountDescription,
        'response' : "Welcome to Genatweetor",
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
    twitter = Twython(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, oauth_token=request.session['oauth_token'], oauth_token_secret=request.session['oauth_token_secret'])
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
    twitter = Twython(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, oauth_token=request.session['oauth_token'], oauth_token_secret=request.session['oauth_token_secret'])
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
    twitter = Twython(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, oauth_token=request.session['oauth_token'], oauth_token_secret=request.session['oauth_token_secret'])
    credentials = twitter.verify_credentials()
    tweetObjects = Tweet.objects.filter(userTweeted_id = user.id)
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
    if os.path.isfile(file):
        if Tweet.objects.filter(userTweeted_id=user.id, usedInTraining=False).exists():
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
        model.train(clean_tweets, total_examples=model.corpus_count, epochs=w2vModel.iter)
        model.save(file)
    return

@is_loggedin
def updateTimeline(request,user):
        tweetObjects = []
        tweets = []
        if not 'count' in request.POST:
            response = {
                'response':"Please enter a value!"
            }
            return response
        else:
            count = int(request.POST['count'])
            twitter = Twython(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, oauth_token=request.session['oauth_token'], oauth_token_secret=request.session['oauth_token_secret'])
            credentials = twitter.verify_credentials()
            SCREEN_NAME = credentials['screen_name']
            try:
                user_timeline = twitter.get_user_timeline(screen_name=SCREEN_NAME, exclude_replies=True, include_rts=True, count=count)
            except TwythonError as e:
                raise Http404(e)
            for tweet in user_timeline:
                id = tweet['id_str']
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
            response = {
                "Deleted!"
            }
            return JsonResponse(list(response), safe=False)
        else:
            response = {
                "OOPS! Something went Wrong! The tweet you tried to delete does not exist!"
            }
            return JsonResponse(list(response), safe=False)
    else:
        response = {
            "OOPS! Something went Wrong!"
        }
        return JsonResponse(list(response), safe=False)

@is_loggedin
def generateTweet(request,user):
    return render(request, 'genatweetor/generateTweet.html')

@is_loggedin
def generateTweets(request,user):
    if 'count' in request.POST:
        count = request.POST['count']
        generatedTweets = []
        twitter = Twython(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, oauth_token=request.session['oauth_token'], oauth_token_secret=request.session['oauth_token_secret'])
        credentials = twitter.verify_credentials()
        twitter_id = credentials['id']
        generator = tweet_generator.PersonTweeter(str(twitter_id), settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
        for i in range(int(count)):
            generated_tweet = generator.generate_random_tweet()
            generatedTweets.append(generated_tweet)
        return JsonResponse(list(generatedTweets), safe=False)

########## POSTING THE RECOMMENDED TWEET TO TWITTER ##########
@is_loggedin # if the user is logged in
def postTweet(request,user):
    tweetText = request.POST['tweetText'] # take the text of th egenerated tweet from the post data
    twitter = Twython(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET, oauth_token=request.session['oauth_token'], oauth_token_secret=request.session['oauth_token_secret'])
    twitter.update_status(status=tweetText)
    response = {"Successful!"}
    return JsonResponse(list(response), safe=False)
##############################################################
@is_loggedin # if the user is logged in
def logout(request,user):
    request.session.flush() # flush the session and return the login template with the context being the response
    return render(request, 'genatweetor/login.html', {'response': "Successfully Signed-out! Thank you for using genatweetor!!"})
