from django.urls import path
from django.conf.urls import url
from . import views

app_name='genatweetor'

urlpatterns = [
    path('', views.index, name='index'),
    path(r'login/', views.login, name='login'),
    path(r'register/', views.register, name='register'),
    path(r'dashboard/',views.dashboard, name='dashboard'),
    path(r'profile/',views.profile, name='profile'),
    path(r'profile/getTwitterProfile/',views.getTwitterProfile, name='getTwitterProfile'),
    path(r'profile/getDjangoProfile/',views.getDjangoProfile, name='getDjangoProfile'),
    path(r'profile/editUserProfile/',views.editUserProfile, name='editProfile'),
    path(r'tweetsArchive/',views.tweetsArchive, name='tweetsArchive'),
    path(r'tweetsArchive/getTweets/',views.getTweets, name='getTweets'),
    path(r'tweetsArchive/updateTimeline/',views.updateTimeline, name='updateTimeline'),
    path(r'tweetsArchive/deleteTweet/<str:tweetID>/', views.deleteTweet, name='deleteTweet'),
    path(r'generateTweet/',views.generateTweet, name='generateTweet'),
    path(r'generateTweet/generateTweets/',views.generateTweets, name='generateTweets'),
    path(r'generateTweet/postTweet/',views.postTweet, name='postTweet'),
    path(r'logout/', views.logout, name="logout")
]
