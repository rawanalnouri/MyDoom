from .models import Notification

def getNotifications(request):
    context = {}
    if request.user:
        userNotifications = Notification.objects.filter(user = request.user)
        context['notifications'] = userNotifications
    return context