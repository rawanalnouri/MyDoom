''' Helpers file contiang methods handling following functionality'''

from walletwizard.models import *

# Function to create a follow requesty notifcation for a user 
def createFollowRequestNotification(toUser, title, message, fromUser):
    FollowRequestNotification.objects.create(
    toUser=toUser,
    fromUser = fromUser,
    title=title,
    message=message,
    type='follow'
    )

# Function to handle following functionality - sends a a follow request to the followee
def toggleFollow(user, followee):
    sentFollowRequest = False

    if followee==user:
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

def follow(currentUser, userToFollow):
    userToFollow.followers.add(currentUser)

def unfollow(currentUser, userToUnfollow):
    userToUnfollow.followers.remove(currentUser)