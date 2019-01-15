from django.conf import settings #then do settings.theVariableYouWantToAccess
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse, Http404
from twython import Twython, TwythonError
import json
# Create your views here.

appname = 'genatweetor'

#LOGIN VIEW
def index(request):
    context ={
        'responseMessage' : "Welcome To genatweetor! Login to Continue!"
    }
    return render(request, 'genatweetor/login.html', context)

def login(request):
    twitter = Twython(settings.CONSUMER_KEY , settings.CONSUMER_SECRET)
    #callback url
    auth = twitter.get_authentication_tokens(callback_url='https://genatweetor.herokuapp.com/dashboard')
    #save oauth tokens into a session variable (a temporary method of storing the oauth variables)
    request.session['oauth_token'] = auth['oauth_token']
    request.session['oauth_token_secret'] = auth['oauth_token_secret']
    #Redirect the user to the url obtained by twitter
    redirect_url = auth['auth_url']
    print(redirect_url)
    # context = {
    #     'responseMessage' : "Successfully Logged in!"
    # }
    return redirect(redirect_url)

def dashboard(request):
     # if user denied authorization
    is_denied = request.session.get('denied')
    if is_denied:
        return HttpResponse("USER DENIED")
    # if not 'oauth_verifier' in request.session:
    #     raise Http404('missing oauth_verifier')
    # oauth_verifier = request.session.get('oauth_verifier')


    twitter = Twython(settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
                      request.session['oauth_token'], request.session['oauth_token_secret'])

    final_step = twitter.get_authorized_tokens(oauth_verifier)

    # store these permanently in database
    OAUTH_TOKEN = final_step['oauth_token']
    OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']

    # get user credential
    twitter = Twython(settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
                       OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    # https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
    data = twitter.verify_credentials()
    user_id = data['id_str']
    name = data['name']
    username = data['screen_name']

    context = {
        'responseMessage' : "Successfully Logged in!"
    }

    return render(request, 'genatweetor/dashboard.html', context)
