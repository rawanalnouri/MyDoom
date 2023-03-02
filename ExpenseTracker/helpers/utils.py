from ExpenseTracker.models import *

# Function to create a basic notifcation for a user 
def createBasicNotification(toUser, title, message):
    Notification.objects.create(
    toUser=toUser,
    title=title,
    message=message,
    type='basic'
    )

# Function to create a share category notifcation for a user 
def createShareCategoryNotification(toUser, title, message, sharedCategory, fromUser):
    ShareCategoryNotification.objects.create(
    toUser=toUser,
    fromUser = fromUser,
    title=title,
    message=message,
    sharedCategory = sharedCategory,
    type='category'
    )

# Function to create a follow requesty notifcation for a user 
def createFollowRequestNotification(toUser, title, message, fromUser):
    FollowRequestNotification.objects.create(
    toUser=toUser,
    fromUser = fromUser,
    title=title,
    message=message,
    type='follow'
    )

''' Function ot handle following functionality'''
def toggleFollow(user, followee):
    """Toggles when self follows a different user."""
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

        # follow(user, followee)

def follow(currentUser, userToFollow):
    userToFollow.followers.add(currentUser)

def unfollow(currentUser, userToUnfollow):
    userToUnfollow.followers.remove(currentUser)