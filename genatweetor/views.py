from django.conf import settings #then do settings.theVariableYouWantToAccess
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse, Http404
from twython import Twython, TwythonError
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
            return render(request, 'genatweetor/login.html', )
        if(user.check_password(password)):
            request.session['username'] = username
            request.session['password'] = password
            #################################################
            twitter = Twython(settings.CONSUMER_KEY , settings.CONSUMER_SECRET)
            #callback url
            auth = twitter.get_authentication_tokens(callback_url='https://genatweetor.herokuapp.com/dashboard')
            #save oauth tokens into a session variable (a temporary method of storing the oauth variables)
            request.session['oauth_token'] = auth['oauth_token']
            request.session['oauth_token_secret'] = auth['oauth_token_secret']
            #Redirect the user to the url obtained by twitter
            redirect_url = auth['auth_url']
            #redirect to twitter login
            return redirect(redirect_url)

def registerUser(request):
    if 'firstName' in request.POST and 'lastName' in request.POST and 'username' in request.POST and 'email' in request.POST and 'dob' in request.POST and 'password' in request.POST:
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        username = request.POST['username']
        userEmail = request.POST['email']
        dateOfBirth = request.POST['dob']
        password = request.POST['password']
        if username == '' or password == '':
            response = {
                'responseMessage' : "Please enter a username and password!"
            }
            return render(request, 'genatweetor/register.html', response)
        user = User(username=username, first_name=firstName,
                       last_name=lastName, email=email, dob=dob)
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            response = {
                'responseMessage' : "Username or E-mail is already Taken, Please enter something different"
            }
            return render(request, 'genatweetor/register.html', response)
    else:
        response = {
            'responseMessage' : "Please fill in all fields!"
        }
        return render(request, 'genatweetor/register.html', response)
#dashboard view
@is_loggedin
def dashboard(request):
     # if user denied authorization
    if 'denied' in request.session:
        return HttpResponse("USER DENIED")
    oauth_verifier = request.GET['oauth_verifier']

    twitter = Twython(settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
                      request.session['oauth_token'], request.session['oauth_token_secret'])

    final_step = twitter.get_authorized_tokens(oauth_verifier)

    # store these permanently in database
    OAUTH_TOKEN = final_step['oauth_token']
    OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']

    # get user credentials
    twitter = Twython(settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
                       OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    # https://developer.twitter.com/en/docs/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
    data = twitter.verify_credentials()
    user_id = data['id_str']
    name = data['name']
    username = data['screen_name']

    response = {
        'name' : name,
        'user': username,
        'responseMessage' : "Successfully Logged in!"
    }

    return render(request, 'genatweetor/dashboard.html', response)
