
from ExpenseTracker.models import Points, Category, SpendingLimit, Expenditure
from django.utils.timezone import datetime, timedelta
from .utils import createBasicNotification
#from
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
        createBasicNotification(request.user,"Points Lost!","3 points lost for going over target")
    elif percentage>10 and percentage<=30:
        addPoints(request,-5)
        createBasicNotification(request.user,"Points Lost!","5 points lost for going over target")
    elif percentage>30 and percentage<=50:
        addPoints(request,-10)
        createBasicNotification(request.user,"Points Lost!","10 points lost for going over target")
    elif percentage>50 and percentage<=70:
        addPoints(request,-15)
        createBasicNotification(request.user,"Points Lost!","15 points lost for going over target")
    elif percentage>70 and percentage<=100:
        addPoints(request,-20)
        createBasicNotification(request.user,"Points Lost!","20 points lost for going over target")
    else:
        addPoints(request,-25)
        createBasicNotification(request.user,"Points Lost!","25 points lost for going over target")



def getTimePeriod(request,category):
    user = request.user
    # need a list of all categories and then do a for loop through them all 
   
    currentSpendingLimit = Category.objects.get(id=category.id).spendingLimit
    period = currentSpendingLimit.timePeriod
    return period

# def getToddaySpending(request,category):
#     currentCategory = Category.objects.get(id=category.id)
#     spent=0.00
#     for expence in currentCategory.expenditures.filter(date=datetime.now().date()):
#         spent+=float(expence.amount)
#     return spent
       

# def dailyTracking(request,category):
#     currentCategory = Category.objects.get(id=category.id)
#     spent = getTodaydaySpending(request,category)
#     if abs(currentCategory.spendingLimit.amount) >= abs(spent):
#         addPoints(request,3)
#         createBasicNotification(request.user,"Points Earned!","5 points for being on target yesterday")
#     else:
#         loosePoints(request, currentCategory.spendingLimit.amount, abs(spent))

# def weeklyTracking(request,category):
#     currentCategory = Category.objects.get(id=category.id)
#     startOfWeek = datetime.now() - timedelta(days=datetime.now().weekday())
#     spent=0.0
#     for expence in currentCategory.expenditures.filter(date__gte=startOfWeek):
#         spent+=float(expence.amount)
#     if abs(currentCategory.spendingLimit.amount) >= abs(spent):
#         addPoints(request,10)
#         createBasicNotification(request.user,"Points Earned!","5 points for being on target this week")

      

# def monthlyTracking(request,category):
#     currentCategory = Category.objects.get(id=category.id)
#     spent=0.0
#     for expence in currentCategory.expenditures.filter(date__month=datetime.now().month-1):
#         spent+=float(expence.amount)
#     if abs(currentCategory.spendingLimit.amount) >= abs(spent):
#         addPoints(request,15)
#         createBasicNotification(request.user,"Points Earned!","5 points for being on target this month")
#     else:
#         loosePoints(request, currentCategory.spendingLimit.amount, abs(spent))
        

    
    
# # even though we check after each expenditure this allows us to add or deduct points at the correct time 

# def trackPoints(request):
#     date = datetime.now()
#     for category in Category.objects.filter(users=request.user):
        
#         if category.spendingLimit.timePeriod=='daily':
#             dailyTracking(request,category)
#         elif category.spendingLimit.timePeriod=='weekly' and date.weekday()==0:
#             weeklyTracking(request,category)
#         elif category.spendingLimit.timePeriod=='monthly' and date.date() == date.replace(day=1).date():
#             #check if its the first day of the month
#             monthlyTracking(request,category)


def checkIfOver(request,category):
    #get latest expenditure check how over they were before
    time=getTimePeriod(request,category)
    currentCategory = Category.objects.get(id=category.id)
    date = datetime.now()
    spent=0.00
    if time=='daily':
        for expence in currentCategory.expenditures.filter(date=datetime.now().date()):
            spent+=float(expence.amount)
        if abs(currentCategory.spendingLimit.amount) >= abs(spent): 
            return (True, spent)
        else:
            return(False, spent)
        
    elif time=='weekly':
        startOfWeek = date - timedelta(days=date.weekday())
        for expence in currentCategory.expenditures.filter(date__gte=startOfWeek):
            spent+=float(expence.amount)
        if abs(currentCategory.spendingLimit.amount) >= abs(spent): 
           return (True, spent)
        else:
            return(False, spent)
          
    elif time=='monthly':
         for expence in currentCategory.expenditures.filter(month__gte=date.month):
            spent+=float(expence.amount)
         if abs(currentCategory.spendingLimit.amount) >= abs(spent): 
           return (True, spent)
         else:
            return(False, spent)
    


def trackPoints(request,category,isOver,totalSpent,newExpenditureAmount):
    currentCategory = Category.objects.get(id=category.id)
    if isOver==False:
        if newExpenditureAmount+totalSpent>currentCategory.spendingLimit:
            loosePoints(request,currentCategory.spendingLimit,newExpenditureAmount+totalSpent)
        else:
            addPoints(request,5)
            createBasicNotification(request.user,"Points Won!","5 points for staying within target :)")
        
    else:
        loosePoints(request,currentCategory.spendingLimit,newExpenditureAmount+totalSpent)


        










    
 

    





























