
from ExpenseTracker.models import Points, Category, SpendingLimit, Expenditure
from django.utils.timezone import datetime, timedelta
#from datetime.datetime import now

def addPoints(request,n):
    user = request.user
    pointsObject = Points.objects.get(user=request.user)
    # currentPoints = pointsObject.pointsNum
    points = Points.objects.get(user=request.user).pointsNum
    pointsObject.pointsNum = points+n
    pointsObject.save()





def loosePoints(request,limit,spent):
    # call add points with a -ve
    # pass in spent and limit find percentage 
    #this function only called if we are over the limit 
    user = request.user
    spentProportion = (spent-limit)/limit 
    percentage = spentProportion*100
    if percentage<=10:
        addPoints(request,-3)
    elif percentage>10 and percentage<=30:
        addPoints(request,-5)
    elif percentage>30 and percentage<=50:
        addPoints(request,-10)
    elif percentage>50 and percentage<=70:
        addPoints(request,-15)
    elif percentage>70 and percentage<=100:
        addPoints(request,-20)
    else:
        addPoints(request,-25)

    
    





def getTimePeriod(request,category):
    user = request.user
    # need a list of all categories and then do a for loop through them all 
   
    currentSpendingLimit = Category.objects.get(id=category.id).spendingLimit
    period = currentSpendingLimit.timePeriod
    return period

def getTodaySpending(request,category):
   
    currentCategory = Category.objects.get(id=category.id)
    spent=0.00
    for expence in currentCategory.expenditures.filter(date=datetime.now().date()):
        spent+=float(expence.amount)
    return spent
       

def dailyTracking(request,category):
    currentCategory = Category.objects.get(id=category.id)
    spent = getTodaySpending(request,category)
    if abs(currentCategory.spendingLimit.amount) >= abs(spent):
        addPoints(request,2)
    else:
        loosePoints(request, currentCategory.spendingLimit.amount, abs(spent))

def weeklyTracking(request,category):
    currentCategory = Category.objects.get(id=category.id)
    spent=0.0
    for expence in currentCategory.expenditures.filter(createdAt__gte=datetime.now()-timedelta(days=7)):
        spent+=float(expence.amount)
    if abs(currentCategory.spendingLimit.amount) >= abs(spent):
        addPoints(request,10)
    else:
        loosePoints(request, currentCategory.spendingLimit.amount, abs(spent))
      

def monthlyTracking(request,category):
    currentCategory = Category.objects.get(id=category.id)
    spent=0.0
    for expence in currentCategory.expenditures.filter(createdAt__gte=datetime.now()-timedelta(months=1)):
        spent+=float(expence.amount)
    if abs(currentCategory.spendingLimit.amount) >= abs(spent):
        addPoints(request,15)
    else:
        loosePoints(request, currentCategory.spendingLimit.amount, abs(spent))

    
    
# even though we check after each expenditure this allows us to add or deduct points at the correct time 

def trackPoints(request):
    date = datetime.now()
    for category in Category.objects.filter(users=request.user):
        
        if category.spendingLimit.timePeriod=='daily':
            dailyTracking(request,category)
        elif category.spendingLimit.timePeriod=='weekly' and date.weekday()==0:
            weeklyTracking(request,category)
        elif category.spendingLimit.timePeriod=='monthly' and date.date() == date.replace(day=1).date():
            #check if its the first day of the month
            monthlyTracking(request,category)

    





























