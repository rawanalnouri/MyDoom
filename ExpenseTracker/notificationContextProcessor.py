from .models import Notification

def getNotifications(request):
    context = {}
    context['unreadNotifications'] = []
    context['readNotifications'] = []
    
    if request.user.is_authenticated:
        unreadNotifications = Notification.objects.filter(user = request.user, isSeen = False)
        readNotifications = Notification.objects.filter(user = request.user, isSeen = True)
        context['unreadNotifications'] = unreadNotifications
        context['latestNotifications'] = unreadNotifications[:3]
        context['readNotifications'] = readNotifications
    
    return context