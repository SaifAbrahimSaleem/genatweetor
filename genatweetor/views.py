from django.shortcuts import render
from django.http import HttpResponse
from twython import Twython
# Create your views here.

appname = 'genatweetor'

# LOGGED IN DECORATOR FOR THE PROGRAM
# def is_loggedIn(view):
#     def logged_in_view(request):
        #PROGRAMMING LOGIC
        # IF THE USERNAME AND PASSWORD IS IN REQUEST.SESSION
        # QUERY THE USERNAME AND THE PASSWORD WITH TWITTER
        # RETURN SUCCESS
        #
        # ELSE
        # DISPLAY TWITTER ERROR

#LOGIN VIEW
def index(request):
    return HttpResponse("HELLO TEST WORLD!")
