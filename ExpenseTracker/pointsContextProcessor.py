from .models import Points

def getPoints(request):
    # Create an empty dictionary to hold the context data
    context = {}
     # If the user is authenticated, get the Points object for that user
    if request.user.is_authenticated:
        points = Points.objects.get(user=request.user)
         # Add the Points object to the context dictionary under the key 'points
        context['points'] = points
    return context