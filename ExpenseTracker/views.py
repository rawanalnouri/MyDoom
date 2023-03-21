from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login,logout
from django.http import Http404
from django.core.paginator import Paginator
from .models import *
from .forms import *
from PersonalSpendingTracker.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models import Q
from .helpers.pointsHelpers import *
from .helpers.notificationsHelpers import *
from .helpers.followHelpers import *
from .helpers.reportsHelpers import *
from .notificationContextProcessor import getNotifications
from django.utils import timezone
from django.utils.timezone import datetime
from datetime import datetime
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import os

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url
        

class CategoryView(LoginRequiredMixin, TemplateView):
    '''View to show an individual category to the logged-in user.'''

    template_name = "category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(id=kwargs["categoryId"])
        paginator = Paginator(category.expenditures.all(), 10)
        page = self.request.GET.get("page")
        expenditures = paginator.get_page(page)

        context = {
            'category': category,
            'expenditures': expenditures,
        }

        categoryLabels = []
        spendingData = []
        for category in Category.objects.filter(id=kwargs["categoryId"]):
            categoryLabels.append(str(category))
            categoryLabels.append("Remaining Budget")
            # append total spent in category to date
            cur = float(category.totalSpent())
            spendingData.append(cur)
            remainingBudget = round(float(category.spendingLimit.amount) - cur, 2)
            if remainingBudget < 0:
                remainingBudget = 0
            spendingData.append(remainingBudget)

        graphData = generateGraph(categoryLabels, spendingData, "doughnut")
        context.update(graphData)

        return context


class EditCategoryView(LoginRequiredMixin, View):
    '''View to edit a category for the logged-in user.'''
    
    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = CategorySpendingLimitForm(user=request.user, instance=category)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = CategorySpendingLimitForm(request.POST, user=request.user, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(self.request, f'Your category \'{category.name}\' was updated successfully.')
            # add points for editing category
            updatePoints(self.request.user, 2)
            createBasicNotification(self.request.user, "New Points Earned!", "2 points earned for editing a new category.")
            return redirect(reverse('category', args=[category.id]))
        else:
            errorMessages = [error for error in form.non_field_errors()] or ["Failed to update category."]
            messages.error(self.request, "\n".join(errorMessages))
            return redirect(reverse('category', args=[kwargs['categoryId']]))


class CreateCategoryView(LoginRequiredMixin, CreateView):
    '''View to create a new category for the logged-in user.'''

    model = Category
    form_class = CategorySpendingLimitForm
    template_name = 'categoryForm.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        category = form.save()
        messages.success(self.request, f'A new category \'{category.name}\' has been successfully created.')
        # add points for creating category
        updatePoints(self.request.user, 5)
        createBasicNotification(self.request.user, "New Points Earned!", "5 points earned for creating a new category.")
        category.save()
        return redirect(reverse('category', args=[category.id]))

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)
    

class DeleteCategoryView(LoginRequiredMixin, View):
    '''View to delete logged-in user's category.'''

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id = kwargs['categoryId'])
        categoryName = category.name
        expenditures = category.expenditures.all()
        for expenditure in expenditures:
            expenditure.delete()
        category.spendingLimit.delete()
        category.delete()
        messages.add_message(request, messages.SUCCESS, f'Your category \'{categoryName}\' was successfully deleted.')
        return redirect('home')


class ShareCategoryView(LoginRequiredMixin, View):
    '''View to send a share request for a category from logged-in user to another user.'''

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = ShareCategoryForm(fromUser=request.user, category=category)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = ShareCategoryForm(fromUser=request.user, category=category, data=request.POST)
        if form.is_valid():
            toUser = form.save()
            messages.add_message(request, messages.SUCCESS, f'A request to share category \'{category.name}\' has been sent to \'{toUser.username}\'.')
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            validationErrors = form.errors.get('__all__', [])
            if validationErrors:
                for error in validationErrors:
                    messages.error(request, error)
            else:
                messages.error(request, 'Failed to send share category request.')
            return redirect(reverse('category', args=[kwargs['categoryId']]))



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
    def get(self, request, *args, **kwargs):
        Notification.objects.get(id=kwargs['notificationId']).delete()
        return redirect(request.META['HTTP_REFERER'])


'''Implements a view for creating expenditures'''
class CreateExpenditureView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = ExpenditureForm(request.user, category)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = ExpenditureForm(request.user, category, request.POST, request.FILES)
        if category and form.is_valid():
            currentCategoryInfo = checkIfOver(category)
            expenditure = form.save()
            messages.success(self.request, f'A new expenditure \'{expenditure.title}\' has been successfully created.')
            trackPoints(self.request.user, category, currentCategoryInfo[0], currentCategoryInfo[1])
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            messages.error(self.request, "Failed to create expenditure.")
            return render(request, 'partials/bootstrapForm.html', {'form': form})


'''Implements a view for updating an expenditure and handling update expenditure form submissions'''
class EditExpenditureView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])     
        expenditure = Expenditure.objects.filter(id=kwargs['expenditureId']).first()
        form = ExpenditureForm(request.user, category, instance=expenditure)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])     
        expenditure = Expenditure.objects.filter(id=kwargs['expenditureId']).first()
        form = ExpenditureForm(request.user, category, request.POST, request.FILES, instance=expenditure)
        if form.is_valid():
            form.save()
            messages.success(self.request, f'Expenditure  \'{expenditure.title}\' was successfully updated.')
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Failed to update expenditure - {field}: {error}.')
            return redirect(reverse('category', args=[kwargs['categoryId']]))
                            

class DeleteExpenditureView(LoginRequiredMixin, View):
    '''View that deletes an expenditure for a user.'''

    def get(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.get(id=kwargs['expenditureId'])
        expenditureTitle = expenditure.title
        # Remove receipt from folder if exists
        receiptPath = os.path.join(settings.MEDIA_ROOT, expenditure.receipt.name)
        if not os.path.isdir(receiptPath):
            os.remove(receiptPath)

        expenditure.delete()
        messages.add_message(request, messages.SUCCESS, f'Your expenditure \'{expenditureTitle}\' was successfully deleted.')
        return redirect(reverse('category', args=[kwargs['categoryId']]))


class SignUpView(LoginProhibitedMixin, View):
    """View that signs up user."""

    redirect_when_logged_in_url = REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            signUpForm = SignUpForm()
            return render(request, 'signUp.html', {'form': signUpForm})

    def post(self, request, *args, **kwargs):
        signUpForm = SignUpForm(request.POST)
        if signUpForm.is_valid():
            user = signUpForm.save()
            points = createPoints(user)
            login(request, user)

            createBasicNotification(user, "New Points Earned!", str(points) + " points earned for signing up!")
            createBasicNotification(user, "Welcome to spending trracker!", "Manage your money here and earn points for staying on track!")

            # assign house to new user
            house = House.objects.get(id = (user.id % 4) + 1)
            user.house = house
            user.save()
            house.memberCount += 1
            house.save()
            housePointsUpdate(user, 50)
           
            return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
        return render(request, 'signUp.html', {'form': signUpForm})


class LogInView(LoginProhibitedMixin, View):
    '''View that logs in a user.'''

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request, *args, **kwargs):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request, *args, **kwargs):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or REDIRECT_URL_WHEN_LOGGED_IN
        if form.is_valid():
            user = form.getUser()
            if user is not None:
                login(request, user)
                # add 5 points if first login of the day
                if user.lastLogin.date() != datetime.now().date():
                    updatePoints(user, 5)
                    createBasicNotification(user, "New Points Earned!", "5 points earned for daily login")
                # update user's 'lastLogin'
                user.lastLogin = timezone.now()
                user.save(update_fields=['lastLogin'])
                return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()
    
    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'logIn.html', {"form": form, 'next': self.next})


class LogOutView(LoginRequiredMixin, View):
    '''View that logs a signed-in user out.'''

    def get(self, request):
        logout(request)
        return redirect('index')


class IndexView(LoginProhibitedMixin, View):
    '''View that is displayed to a user before signing in.'''

    redirect_when_logged_in_url = REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return render(request, 'index.html')


def generateGraph(categories, spentInCategories, type, graphNum = ''):
    dict = {f'labels{graphNum}': categories, f'data{graphNum}': spentInCategories, f'type{graphNum}':type}
    return dict


class HomeView(LoginRequiredMixin, View):
    '''View that handles and shows the Home page to the user.'''

    def get(self, request):
        categories = []
        totalSpent = []

        for category in Category.objects.filter(users__in=[request.user]):
            categories.append(str(category))
            # calculate total spent this month per category
            categoryExpenseThisMonth = 0.0
            today = datetime.now()
            for expense in category.expenditures.filter(date__month=today.month):
                    categoryExpenseThisMonth += float(expense.amount)
            totalSpent.append(round(categoryExpenseThisMonth, 2))

        houses =[]
        pointTotals = []
        for house in House.objects.all():
            houses.append(house.name)
            pointTotals.append(house.points)
        dict = generateGraph(categories, totalSpent,'pie')
        dict.update(generateGraph(houses, pointTotals,'doughnut', 2))

        context = {**dict, **{
            'month': datetime.now().strftime('%B'),
            'year': datetime.now().strftime('%Y'),
            'points': Points.objects.get(user=request.user),
        }}

        return render(request, "home.html", context)


class ScoresView(LoginRequiredMixin, ListView):
    '''View that handles and shows the Scores page to the user.'''

    model = Points
    template_name = "scores.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orderedPoints = Points.objects.all().order_by('-count')
        paginator = Paginator(orderedPoints, self.paginate_by)
        pageNumber = self.request.GET.get('page')
        context['houses'] = House.objects.order_by('-points')
        context['points'] = paginator.get_page(pageNumber)
        context['topPoints'] = orderedPoints[:4]
        return context


class ReportsView(LoginRequiredMixin, View):
    '''View that handles and shows the Reports page to the user.'''

    def get(self, request):
        form = ReportForm(user=request.user)
        graphData = generateGraph([], [], 'bar')
        graphData.update({"form": form, "text": "Waiting for your selection..."})
        return render(request, "reports.html", graphData)

    def post(self, request):
        today = datetime.now()
        form = ReportForm(request.POST, user=request.user)
        categories = []
        totalSpent = []
        createdArrays = []
        if form.is_valid():
            timePeriod = form.cleaned_data.get('timePeriod')
            selectedCategories = form.cleaned_data.get('selectedCategory')

            createdArrays = createArraysData(selectedCategories, timePeriod)
            categories = createdArrays[0]
            totalSpent = createdArrays[1]

            graphData = generateGraph(categories, totalSpent, 'bar')
            graphData.update({"form": form, "text": f"An overview of your spending within the last {timePeriod}."})

            # generate a graph for historical data
            first_day_this_month = today.replace(day=1)
            first_day_next_month = (first_day_this_month + timedelta(days=32)).replace(day=1)
            first_day_twelve_months_ago = first_day_next_month - relativedelta(years=1)
            data1 = createArraysData(selectedCategories, timePeriod, first_day_twelve_months_ago,  [365, 52, 12])

            graphData.update({'data1':data1})
            graphData.update({'text2':"Comparison to average over last 12 months"})

            six_months_ago = today + relativedelta(months=-6)
            data2 = createArraysData(selectedCategories, timePeriod, six_months_ago,  [180, 24, 6])

            graphData.update({'data2':data2})
            graphData.update({'text2':f"Compare your average spendings per {timePeriod} in the past"})

            three_months_ago = today + relativedelta(months=-3)
            data3 = createArraysData(selectedCategories, timePeriod, three_months_ago,  [90, 12, 3])

            graphData.update({'data3':data3})
            graphData.update({'text3':f"Your average spending per {timePeriod}"})

            return render(request, "reports.html", graphData)
        else:
            graphData = generateGraph(categories, totalSpent, 'bar')
            graphData.update({"form": form, "text": "Waiting for your selection..."})
            return render(request, "reports.html", graphData)


class ProfileView(LoginRequiredMixin, View):
    '''View to display logged-in user's profile.'''

    def get(self, request):
        return render(request,'profile.html')


class EditProfileView(LoginRequiredMixin, View):
    '''View to edit logged-in user's profile.'''

    def get(self,request):
        newForm = EditProfile(instance=request.user)
        return render(request, "editProfile.html", {'form': newForm})

    def post(self,request):
        form = EditProfile(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            return render(request, "editProfile.html", {'form': form})


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    '''View to change logged-in user's password.'''

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


class NotificationsView(LoginRequiredMixin, View):
    '''View to display logged-in user's notifications.'''

    def get(self,request):
        context = {}
        allNotifications = getNotifications(request)
        # add pagination - show 5 unread notifications per page
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

'''View function to allow logged-in user to filter users by username.'''
@login_required
def searchUsers(request):
    query = request.GET.get('q')
    if query is None:
        users = User.objects.all()
    else:
        users = User.objects.filter(
            Q(username__istartswith=query)
        )
    return render(request, 'partials/users/searchResults.html', {'users': users})


class SetOverallSpendingLimitView(LoginRequiredMixin, View):
    '''View function to update or set the logged-in user's overall spending limit.'''

    def get(self, request, *args, **kwargs):
        form = OverallSpendingForm(user=request.user)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = OverallSpendingForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Your overall spending limit has been updated successfully.")
            return redirect('home')
        else:
            validationErrors = form.errors.get('__all__', [])
            if validationErrors:
                for error in validationErrors:
                    messages.error(request, error)
            else:
                messages.error(request, 'Failed to update overall spending limit.')
            return redirect('home')