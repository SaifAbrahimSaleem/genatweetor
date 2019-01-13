from django.conf import settings #then do settings.theVariableYouWantToAccess
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from twython import Twython, TwythonError
import json
# Create your views here.

appname = 'genatweetor'
#NEEDS TO BE LOCAL HOST
CALLBACK_URL = 'https://genatweetor.herokuapp.com/dashboard'

# LOGGED IN DECORATOR FOR THE PROGRAM
# def is_loggedIn(view):
#     def logged_InView(request):
#         if 'username' in request.session:
#         username = request.session['username']
#         try:

        #PROGRAMMING LOGIC
        # IF THE USERNAME or email IS IN REQUEST.SESSION
        # QUERY THE USERNAME AND THE PASSWORD WITH TWITTER
        # RETURN SUCCESS
        #
        # ELSE
        # DISPLAY TWITTER ERROR

# def authenticateConnection(request, user):
#     OAUTH_TOKEN = settings.auth['oauth_token']
#     OAUTH_TOKEN_SECRET = settings.auth['oauth_token_secret']
#     authorisedURL = settings.auth['auth_url']
#       redirect(authorisedURL)
########## HANDLING CALLBACK ##########
#     oauth_verifier = request.GET['oauth_verifier']
#     twitter = Twython(settings.APP_KEY, settings.APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
#     final_step = twitter.get_authorized_tokens(oauth_verifier)
#     OAUTH_TOKEN = final_step['oauth_token']
#     OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']

#LOGIN VIEW
def index(request):
    context ={
        'responseMessage' : "Welcome To genatweetor! Login to Continue!"
    }
    return render(request, 'genatweetor/login.html', context)

def login(request):
    twitter = Twython(settings.credentials['CONSUMER_KEY'],settings.credentials['CONSUMER_SECRET'])
    auth = twitter.get_authentication_tokens(callback_url=CALLBACK_URL)
    context = {
        'responseMessage' : "Successfully Logged in!"
    }
    return render(request, 'genatweetor/login.html', context)

def dashboard(request):
    context = {
        'responseMessage' : "Successfully Logged in!"
    }
    return HttpResponse(request, 'genatweetor/dashboard.html', context)
