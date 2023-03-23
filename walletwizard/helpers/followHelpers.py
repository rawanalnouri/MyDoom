'''Helpers file for following functionality.'''
from walletwizard.models import *

def createFollowRequestNotification(toUser, title, message, fromUser):
    FollowRequestNotification.objects.create(
        toUser=toUser,
        fromUser = fromUser,
        title=title,
        message=message,
        type='follow'
    )

def toggleFollow(user, followee):
    sentFollowRequest = False

    if followee == user:
        return
    if user.isFollowing(followee):
        unfollow(user, followee)
        return sentFollowRequest
    else:
        toUser = followee
        fromUser = user
        title = "New follow request!"
        message = fromUser.username + " wants to follow you"
        createFollowRequestNotification(toUser, title, message, fromUser)
        sentFollowRequest = True
        return sentFollowRequest

def follow(user, followee):
    followee.followers.add(user)

def unfollow(user, followee):
    followee.followers.remove(user)