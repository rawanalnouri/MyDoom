from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.core.paginator import Paginator
from ExpenseTracker.models import *
from ExpenseTracker.forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from ExpenseTracker.notificationContextProcessor import getNotifications
    

class ProfileView(LoginRequiredMixin, View):
    '''View that handles requests to the profile page'''

    def get(self, request):
        return render(request,'profile.html')
    
    def handle_no_permission(self):
        return redirect('logIn')


class EditProfileView(LoginRequiredMixin, View):
    '''View that handles requests to the edit profile page'''

    def get(self,request):
        newForm = EditProfile(instance=request.user)
        return render(request, "editProfile.html", {'form': newForm})

    def post(self,request):
        form = EditProfile(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        else:
            return render(request, "editProfile.html", {'form': form})

    def handle_no_permission(self):
        return redirect('logIn')
    
    
class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'changePassword.html'
    form_class = PasswordChangeForm

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('home')
    
    def handle_no_permission(self):
        return redirect('logIn')


class NotificationsView(LoginRequiredMixin, View):

    def get(self,request):
        context = {}
        allNotifications = getNotifications(request)
        # adding pagination
        unreadPaginator = Paginator(allNotifications['unreadNotifications'], 5) # Show 5 unread notifications per page
        unreadPage = self.request.GET.get('page')
        unreadNotificationPaginated = unreadPaginator.get_page(unreadPage)
        context['unreadNotificationsPaginated'] = unreadNotificationPaginated

        readPaginator = Paginator(allNotifications['readNotifications'], 5) # Show 5 read notifications per page
        readPage = self.request.GET.get('page')
        readNotificationPaginated = readPaginator.get_page(readPage)
        context['readNotificationsPaginated'] = readNotificationPaginated

        return render(request, "notifications.html", context) 
    
    def handle_no_permission(self):
        return redirect('logIn')


class EditNotificationsView(LoginRequiredMixin, View):
    '''Implements a view function for marking notifications as read'''

    def dispatch(self, request, *args, **kwargs):
        notification = Notification.objects.get(id=kwargs['notificationId'])
        notification.isSeen = not notification.isSeen
        notification.save()

        # Making the user stay on whichever page they called this request  
        return redirect(request.META['HTTP_REFERER'])
    
    def handle_no_permission(self):
        return redirect('logIn')


class DeleteNotificationsView(LoginRequiredMixin, View):
    '''Implements a view function for deleting a notification'''

    def dispatch(self, request, *args, **kwargs):
        notification = Notification.objects.get(id=kwargs['notificationId'])
        if notification.isSeen:
            Notification.objects.get(id=kwargs['notificationId']).delete()
        return redirect("notifications")  
    
    def handle_no_permission(self):
        return redirect('logIn')


class DeleteAllNotifications(LoginRequiredMixin, View):
    '''Implements a view function for deleting all read notifications'''

    def dispatch(self, request, *args, **kwargs):
        Notification.objects.filter(toUser = request.user, isSeen = True).delete()
        return redirect("notifications")  
    
    def handle_no_permission(self):
        return redirect('logIn')
    

class AcceptCategoryShareView(LoginRequiredMixin, View):
    '''Implements a view for accepting a share category requests'''

    def dispatch(self, request, *args, **kwargs):
        notification = ShareCategoryNotification.objects.get(id=kwargs['notificationId'])
        toUser = notification.toUser
        category = notification.sharedCategory

        # Sharing the category
        category.users.add(toUser)
        category.save()
        toUser.categories.add(category)
        toUser.save()
        messages.add_message(request, messages.SUCCESS, "Successfully accepted share request ")

        # Sending accept notification
        fromUser = notification.fromUser
        title = 'Category share request accepted'
        message = toUser.username + " has accepted your request to share '"+ category.name +"'"
        createBasicNotification(fromUser, title, message)

        # Deleting the notification after it has been accepted
        return redirect('declineRequest', notificationId = notification.id)

    def handle_no_permission(self):
        return redirect('logIn')
    

class DeclineRequestView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        Notification.objects.get(id=kwargs['notificationId']).delete()
        return redirect(request.META['HTTP_REFERER'])

    def handle_no_permission(self):
        return redirect('logIn')


class UserListView(LoginRequiredMixin, ListView):
    '''View that shows a list of all users and allows user to filter users based on username'''

    model = User
    template_name = 'users.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""

        context = super().get_context_data(*args, **kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        users = paginator.get_page(page)
        context['users'] = users
        return context
    
    def handle_no_permission(self):
        return redirect('logIn')


def searchUsers(request):
    query = request.GET.get('q')
    if query is None:
        users = User.objects.all()
    else: 
        users = User.objects.filter(
            Q(username__istartswith=query)
        )
    return render(request, 'partials/users/searchResults.html', {'users': users})

    
class ShowUserView(LoginRequiredMixin, DetailView):
    """View that shows individual user details."""

    model = User
    template_name = 'showUser.html'
    context_object_name = "otherUser"
    pk_url_kwarg = 'userId'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""

        context = super().get_context_data(*args, **kwargs)
        user = self.get_object()
        context['following'] = self.request.user.isFollowing(user)
        context['followable'] = (self.request.user != user)
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to users if userId invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect(reverse('users'))
    
    def handle_no_permission(self):
        return redirect('logIn')
    

class FollowToggleView(LoginRequiredMixin, View):
    '''View that handles follow/unfollow user functionality'''

    def get(self, request, userId, *args, **kwargs):
        currentUser = request.user
        try:
            followee = User.objects.get(id=userId)
            sentFollowRequest = toggleFollow(currentUser, followee)
            if sentFollowRequest:
                messages.add_message(request, messages.SUCCESS, "Successfully sent follow request to "+ followee.username)
        except ObjectDoesNotExist:
            return redirect('users')
        else:
            return redirect('showUser', userId=userId)
    
    def handle_no_permission(self):
        return redirect('logIn')


class AcceptFollowRequestView(LoginRequiredMixin, View):
    '''Implements a view for accepting a follow request category requests'''

    def dispatch(self, request, *args, **kwargs):
        notification = FollowRequestNotification.objects.get(id=kwargs['notificationId'])
        toUser = notification.toUser
        fromUser = notification.fromUser
        follow(fromUser, toUser)
        messages.add_message(request, messages.SUCCESS, "Successfully accepted follow request ")

        # Sending accept notification
        title = 'Follow request accepted'
        message = toUser.username + " has accepted your follow request"
        createBasicNotification(fromUser, title, message)

        # Deleting notification after being accepted
        return redirect('declineRequest', notificationId = notification.id)
    
    def handle_no_permission(self):
        return redirect('logIn')