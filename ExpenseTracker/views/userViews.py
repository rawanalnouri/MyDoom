"""Views that are user-related but do not deal with user profile."""
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.core.paginator import Paginator
from ExpenseTracker.models import User, FollowRequestNotification
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from ExpenseTracker.helpers.notificationsHelpers import createBasicNotification
from ExpenseTracker.helpers.followHelpers import toggleFollow, follow


class ShowUserView(LoginRequiredMixin, DetailView):
    '''View that shows individual user details.'''

    model = User
    template_name = 'showUser.html'
    context_object_name = "otherUser"
    pk_url_kwarg = 'userId'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        '''Generate content to be displayed in the template.'''

        context = super().get_context_data(*args, **kwargs)
        user = self.get_object()
        context['following'] = self.request.user.isFollowing(user)
        context['followable'] = (self.request.user != user)
        return context

    def get(self, request, *args, **kwargs):
        '''Handle get request, and redirect to users if userId invalid.'''

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect(reverse('users'))


class FollowToggleView(LoginRequiredMixin, View):
    '''View that handles follow request and unfollow user functionality'''

    def get(self, request, userId, *args, **kwargs):
        currentUser = request.user
        try:
            followee = User.objects.get(id=userId)
            sentFollowRequest = toggleFollow(currentUser, followee)
            if sentFollowRequest:
                messages.add_message(request, messages.SUCCESS, f'A follow request has been sent to {followee.username}.')
        except ObjectDoesNotExist:
            return redirect('users')
        else:
            return redirect('showUser', userId=userId)


class AcceptFollowRequestView(LoginRequiredMixin, View):
    '''View to accept a follow request from another user for the logged-in user.'''

    def get(self, request, *args, **kwargs):
        notification = FollowRequestNotification.objects.get(id=kwargs['notificationId'])
        toUser = notification.toUser
        fromUser = notification.fromUser
        follow(fromUser, toUser)
        messages.add_message(request, messages.SUCCESS, "Successfully accepted follow request.")
        # send accept notification
        title = 'Follow request accepted'
        message = f'{toUser.username} has accepted your follow request.'
        createBasicNotification(fromUser, title, message)
        # delete notification after being accepted
        return redirect('deleteRequest', notificationId = notification.id)
    

class UserListView(LoginRequiredMixin, ListView):
    '''View to show the list of all users.'''

    model = User
    template_name = 'users.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        '''Generate content to be displayed in the template.'''

        context = super().get_context_data(*args, **kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        users = paginator.get_page(page)
        context['users'] = users
        return context


@login_required
def searchUsers(request):
    '''View function to allow logged-in user to filter users by username.'''

    query = request.GET.get('q')
    if query is None:
        users = User.objects.all()
    else:
        users = User.objects.filter(
            Q(username__istartswith=query)
        )
    return render(request, 'partials/users/searchResults.html', {'users': users})
