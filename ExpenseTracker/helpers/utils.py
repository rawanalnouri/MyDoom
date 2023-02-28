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

# Function to create a share category notifcation for a user 
def createFriendRequestNotification(toUser, title, message, fromUser):
    ShareCategoryNotification.objects.create(
    toUser=toUser,
    fromUser = fromUser,
    title=title,
    message=message,
    type='friend'
    )