from ExpenseTracker.models import Points, Notification

'''Reports'''

def generateGraph(categories, spentInCategories, type):
    dict = {'labels': categories, 'data': spentInCategories, 'type':type}
    return dict