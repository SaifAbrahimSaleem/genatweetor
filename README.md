# Final Year Project – Supporting Materials Student Name: Saif Saleem   Supervisor: Dr. Laurissa Tokarchuk Student ID: 160437333
# Genatweetor: Exploring engagement and tweet generation through recommender systems using machine learning 

README 

Link to Deployment:  
https://genatweetor.herokuapp.com 

Developed using a Windows based Virtual Environment for debugging and testing. This source code has been configured for the deployment environment on Heroku so only if absolutely necessary, below are the instructions to setup, configure and run the source code. Some deployment settings tend to interfere with local running hence why the preferred method of running is through the deployed link. 

Instructions for Running Locally (if necessary):  
# Setup 
 Create a virtual environment 
 Using a command line interface, move to the root directory (cd ../../Projectfolder/Genatweetor) 
 Activate the virtual environment 
 Run “pip install -r requirements.txt” to download and install the packages to the virtual environment Configurations:  
 Using an IDE such as atom, open the settings.py file 
 Scroll down to allowed hosts and remove the “ ‘.herokuapp.com’ ” value from ALLOWED_HOSTS=[‘.herokuapp.com’] Running the application: 
 Run the command “python manage.py runserver” 
 Open google chrome and type ‘127.0.0.1:8000’  

# Typical usage instructions:  
These instructions can be followed for running locally and through deployment usage. 
 Upon running the application, the index page will be loaded which is a login screen Creating an Account: 
 Click on “Haven’t got an account? Register Here!” and follow the registration form. 
 When submitted, the application will redirect back to the index. Use the username and password from registration to log in. 
 Authenticate the Django account via the twitter portal. Sign in using a Twitter Account. Sensitive Twitter data is dealt with by Twitter through their sign-in portal. 

# Usage: 
 Once logged in through twitter, the dashboard will load. Because there are no tweets associated with the account, engagement statistics will be 0.  
 Once the dashboard is loaded, for engagement statistics, click on “Tweets Archive” located on the left-side navbar. 
 Enter a number in the update timeline input bar (max 100). 
 Once all of the tweets have loaded, if any tweets need to be deleted, click on the tweet card and then click on “Delete Tweet”. Then click on the home icon, where the dashboard will be reloaded. This time it will load slower due to engagement, k-means score and silhouette scores being calculated. 

# Tweet Generation: 
 To generate tweets, click on “Generate Tweet” located under the “Tweets Archive” button on the left-side navbar. 
 Similar to the update timeline method, input a number in the input bar and a list of tweet cards will generate with generated tweet text associated with it. 
 Choose a tweet to post. Edit the tweet if necessary and add “- Genatweetor” to the end of the tweet text. 
 Click on post. If successful, an alert will appear with the message “SUCCESSFUL!” on it. Click on ok 
 Logout of the application by clicking on the logout button located below the “Generate Tweet” button on the left-side navbar. 
 To check to see if a tweet has been posted to your timeline, log into Twitter and search the term “Genatweetor” for your tweet alongside all of the other generated tweets which have been posted to Twitter. 
# Admin: 
The admin section of the application is a representation of saved entities and attributes in web form.  
 To view the back end of the application copy and paste the link:  
    https://genatweetor.herokuapp.com/admin 
            OR (if running locally) 
             127.0.0.1:8000/admin 
             
 Login using the following credentials: 
# Username: Administrator 
# Password: Admin123 