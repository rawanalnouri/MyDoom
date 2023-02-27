from ExpenseTracker.models import *

# Function to create a notifcation for a user 
def createNotification(user, title, message):
    Notification.objects.create(
    user=user,
    title=title,
    message=message
    )
