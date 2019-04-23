from django.conf import settings #then do settings.theVariableYouWantToAccess
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404
from twython import Twython, TwythonError
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import User, Tweet
from datetime import datetime, timezone
import json
# Create your views here.

appname = 'genatweetor'

def is_loggedin(view):
    def loggedin_view(request):
        #Check to see if the user's username is in the request
        if 'username' in request.session:
            username = request.session['username']
            try:
                u = User.objects.get(username=username)
            except User.DoesNotExist:
                raise Http404('User does not exist')
            return view(request, u)
        else:
            return render(request, 'genatweetor/login.html')
    return loggedin_view

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
        user = User(
            username=username,
            first_name=firstName,
            last_name=lastName,
            email=email,
            dob=dateOfBirth,
        )

        user.set_password(password)
        try:
            user.save()
            # If any credentials are already saved to the database
        except IntegrityError as e:
            response = {
                'responseMessage' : "Username or E-mail is already Taken, Please enter something different"
                }
            print(e)
            return render(request, 'genatweetor/register.html', response)
        response = {
            'responseMessage' : "You have been successfully registered! You can now Login!"
        }
        return render(request, 'genatweetor/login.html', response)
    response = {
        'responseMessage' : "You have been successfully registered! You can now Login!"
    }
    return render(request, 'genatweetor/login.html', response)

#dashboard view
@is_loggedin
def dashboard(request, user):
     # if user denied authorization
    if 'denied' in request.session:
        return HttpResponse("USER DENIED")

    twitter = Twython(settings.APP_KEY, settings.APP_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
    credentials = twitter.verify_credentials()
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
        'responseMessage' : "Welcome to Genatweetor"
    }

    return render(request, 'genatweetor/dashboard.html', response)

@is_loggedin
def setting(request, user):
    return render(request, 'genatweetor/settings.html')

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
    print(query)
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
            tweetAttributes = {
                'tweetID':tweet.id,
                'tweetText':text,
                'tweetDate':date,
                'tweetedBy':user
            }
            tweets.append(tweetAttributes)
        return JsonResponse(tweets, safe=False)
    else:
        print("entered else")
        response = []
        response.append(list(tweetObjects))
        return JsonResponse(response, safe=False)
@is_loggedin
def updateTimeline(request,user):
        # get user credentials
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
                #print(user_timeline)
            except TwythonError as e:
                raise Http404(e)
            for tweet in user_timeline:
                id = tweet['id_str']
                if Tweet.objects.filter(tweetID=id).exists():
                    continue
                text = tweet['text']
                date = datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=timezone.utc).astimezone(tz=timezone.utc).strftime('%Y-%m-%d')
                userTweet = Tweet(userTweeted=user,tweetID=id,tweetedBy=SCREEN_NAME, tweetText=text, tweetDate=date)
                tweetObjects.append(userTweet)
                try:
                    userTweet.save()
                except IntegrityError as e:
                    print("IntegrityError")
                    print(e)
                    continue
            for tweet in tweetObjects:
                text = tweet.getTweetText()
                date = tweet.getDateTweeted()
                user = tweet.getUserTweeted()
                tweetAttributes = {
                    'tweetText':text,
                    'tweetDate':date,
                    'tweetedBy':user
                }
                tweets.append(tweetAttributes)
            return JsonResponse(tweets, safe=False)

def deleteTweet(request, id):
    #get the tweet text and search for it in the database
    #delete the tweet object
    if request.method == "DELETE":
        if Tweet.objects.filter(id=id).exists():
            delTweet = Tweet.objects.filter(id=id)
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
def statistics(request, user):
    return render(request, 'genatweetor/statistics.html')

@is_loggedin
def generateTweet(request, user):
    return render(request, 'genatweetor/generateTweet.html')
