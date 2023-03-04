from ExpenseTracker.models import Points, Notification

'''Reports'''

def generateGraph(categories, spentInCategories, type):
    dict = {'labels': categories, 'data': spentInCategories, 'type':type}
    return dict

'''Points tracking'''

def addPoints(user, n):
    pointsObject = Points.objects.get(user = user)
    # currentPoints = pointsObject.pointsNum
    points = Points.objects.get(user = user).pointsNum
    pointsObject.pointsNum = points + n
    pointsObject.save()

'''Notifications'''

def createNotification(user, title, message):
    Notification.objects.create(
    user=user,
    title=title,
    message=message
)