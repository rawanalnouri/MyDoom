from ..models import Points

def getPoints(request):
    context = {}
    if request.user.is_authenticated:
        points = Points.objects.get(user=request.user)
        context['points'] = points
    return context