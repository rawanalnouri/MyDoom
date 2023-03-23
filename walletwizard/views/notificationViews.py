"""Views that handle basic notifications and notification requests."""
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from walletwizard.models import ShareCategoryNotification, Notification
from walletwizard.helpers.notificationsHelpers import createBasicNotification
from walletwizard.contextProcessors.notificationsContextProcessor import getNotifications

        
class AcceptShareCategoryView(LoginRequiredMixin, View):
    '''View to accept a share category request from another user for the logged-in user.'''

    def get(self, request, *args, **kwargs):
        notification = ShareCategoryNotification.objects.get(id=kwargs['notificationId'])
        toUser = notification.toUser
        category = notification.sharedCategory

        # Share the category 
        category.users.add(toUser)
        category.save()
        toUser.categories.add(category)
        toUser.save()
        messages.add_message(request, messages.SUCCESS, f'Share category request for category \'{category.name}\' was accepted successfully.')

        # Send accept notification 
        fromUser = notification.fromUser
        title = 'Category share request accepted'
        message = f'{toUser.username} has accepted your request to share the category \'{category.name}\'.'
        createBasicNotification(fromUser, title, message)

        # Delete the notification after it has been accepted
        return redirect('deleteRequest', notificationId = notification.id)


class DeleteRequestView(LoginRequiredMixin, View):
    '''View that deletes a notification request and redirects to the previous page.'''

    def get(self, request, *args, **kwargs):
        Notification.objects.get(id=kwargs['notificationId']).delete()
        return redirect(request.META['HTTP_REFERER'])


class NotificationsView(LoginRequiredMixin, View):
    '''View to display logged-in user's notifications.'''

    def get(self,request):
        context = {}
        allNotifications = getNotifications(request)
        # Add pagination - show 5 unread notifications per page
        unreadPaginator = Paginator(allNotifications['unreadNotifications'], 5)
        unreadPage = self.request.GET.get('page')
        unreadNotificationPaginated = unreadPaginator.get_page(unreadPage)
        context['unreadNotificationsPaginated'] = unreadNotificationPaginated
        # Show 5 read notifications per page
        readPaginator = Paginator(allNotifications['readNotifications'], 5)
        readPage = self.request.GET.get('page')
        readNotificationPaginated = readPaginator.get_page(readPage)
        context['readNotificationsPaginated'] = readNotificationPaginated

        return render(request, "notifications.html", context)


class EditNotificationsView(LoginRequiredMixin, View):
    '''View to mark logged-in user's notifications as read.'''

    def get(self, request, *args, **kwargs):
        notification = Notification.objects.get(id=kwargs['notificationId'])
        notification.isSeen = not notification.isSeen
        notification.save()

        # Make logged-in user stay on whichever page they called this request
        return redirect(request.META['HTTP_REFERER'])


class DeleteNotificationsView(LoginRequiredMixin, View):
    '''View to delete a logged-in user's notification.'''

    def get(self, request, *args, **kwargs):
        notification = Notification.objects.get(id=kwargs['notificationId'])
        if notification.isSeen:
            Notification.objects.get(id=kwargs['notificationId']).delete()
        return redirect("notifications")


class DeleteAllNotifications(LoginRequiredMixin, View):
    '''View to delete all of logged-in user's notifications.'''

    def get(self, request, *args, **kwargs):
        Notification.objects.filter(toUser = request.user, isSeen = True).delete()
        return redirect("notifications")