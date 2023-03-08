from ExpenseTracker.models import *
from datetime import datetime
from datetime import timedelta

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

# Function to compute spending in expenditures based on time period 
def computeTotalSpent(timePeriod, expenditures):
    total = 0.0
    today = datetime.now()
    if timePeriod == 'daily':
        for expense in expenditures.filter(date__day=today.day):
            total += float(expense.amount)
    elif timePeriod == 'weekly':
        startOfWeek = today - timedelta(days=today.weekday())
        for expense in expenditures.filter(date__gte=startOfWeek):
            total += float(expense.amount)
    elif timePeriod == 'monthly':
        for expense in expenditures.filter(date__month=today.month):
            total += float(expense.amount)
    elif timePeriod == 'yearly':
        for expense in expenditures.filter(date__year=today.year):
            total += float(expense.amount)
    return total