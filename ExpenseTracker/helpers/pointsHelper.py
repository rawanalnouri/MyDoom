
from ExpenseTracker.models import Points
from django.utils.timezone import datetime

def addPoints(request,n):
    user = request.user
    pointsObject = Points.objects.get(user=request.user)
    # currentPoints = pointsObject.pointsNum
    points = Points.objects.get(user=request.user).pointsNum
    pointsObject.pointsNum = points+n
    pointsObject.save()












