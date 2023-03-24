''''Helpers file to create different types of notifications.'''
from walletwizard.models import Notification, ShareCategoryNotification, FollowRequestNotification

def createBasicNotification(toUser, title, message):
    Notification.objects.create(
        toUser=toUser,
        title=title,
        message=message,
        type='basic'
    )

def createShareCategoryNotification(toUser, title, message, sharedCategory, fromUser):
    ShareCategoryNotification.objects.create(
        toUser=toUser,
        fromUser=fromUser,
        title=title,
        message=message,
        sharedCategory=sharedCategory,
        type='category'
    )

def createFollowRequestNotification(toUser, title, message, fromUser):
    FollowRequestNotification.objects.create(
        toUser=toUser,
        fromUser=fromUser,
        title=title,
        message=message,
        type='follow'
    )