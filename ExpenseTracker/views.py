from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout
from django.http import Http404
from django.core.paginator import Paginator
from .models import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .helpers.pointsHelpers import *
from .helpers.notificationsHelpers import *
from .helpers.followHelpers import *
from .helpers.reportsHelpers import *
from .notificationContextProcessor import getNotifications
from django.utils import timezone
from django.utils.timezone import datetime
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import os

'''Displays a specific category and handles create expenditure and edit category form submissions.'''
class CategoryView(LoginRequiredMixin, TemplateView):

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

    def handle_no_permission(self):
        return redirect("logIn")


'''Implements a view for editing categories'''
class EditCategoryView(LoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = CategorySpendingLimitForm(user=request.user, instance=category)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = CategorySpendingLimitForm(request.POST, user=request.user, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(self.request, "Category updated successfully.")
            # add points
            updatePoints(self.request.user,5)
            createBasicNotification(self.request.user, "New Points Earned!", "5 points earned for creating a new category")
            return redirect(reverse('category', args=[category.id]))
        else:
            errorMessages = [error for error in form.non_field_errors()] or ["Failed to update category."]
            messages.error(self.request, "\n".join(errorMessages))
            return redirect(reverse('category', args=[kwargs['categoryId']]))

    def handle_no_permission(self):
        return redirect('logIn')


'''Implements a view for creating a new category using a form'''
class CreateCategoryView(LoginRequiredMixin, CreateView):

    model = Category
    form_class = CategorySpendingLimitForm
    template_name = 'categoryForm.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        category = form.save()
        messages.success(self.request, "Successfully Created Category")
        # add points
        updatePoints(self.request.user,5)
        createBasicNotification(self.request.user, "New Points Earned!", "5 points earned for creating a new category")
        category.save()
        return redirect(reverse('category', args=[category.id]))

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)

    def handle_no_permission(self):
        return redirect('logIn')
    

'''Implements a view for deleting an expenditure'''
class DeleteCategoryView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id = kwargs['categoryId'])
        expenditures = category.expenditures.all()
        for expenditure in expenditures:
            expenditure.delete()
        category.spendingLimit.delete()
        category.delete()
        messages.add_message(request, messages.SUCCESS, "Category successfully deleted")
        return redirect('home')

    def handle_no_permission(self):
        return redirect('logIn')


'''Implements a view for sharing categories'''
class ShareCategoryView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = ShareCategoryForm(fromUser=request.user, category=category)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = ShareCategoryForm(fromUser=request.user, category=category, data=request.POST)
        if form.is_valid():
            toUser = form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully sent request to share '"+ category.name +"' with "+ toUser.username)
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            validationErrors = form.errors.get('__all__', [])
            if validationErrors:
                for error in validationErrors:
                    messages.error(request, error)
            else:
                messages.error(request, 'Failed to send share category request.')
            return redirect(reverse('category', args=[kwargs['categoryId']]))

    def handle_no_permission(self):
        return redirect('logIn')


'''Implements a view for accepting a share category requests'''
class AcceptShareCategoryView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
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
    def get(self, request, *args, **kwargs):
        Notification.objects.get(id=kwargs['notificationId']).delete()
        return redirect(request.META['HTTP_REFERER'])

    def handle_no_permission(self):
        return redirect('logIn')


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
            messages.success(self.request, "Expenditure created successfully.")
            form.save()
            trackPoints(self.request.user, category,currentCategoryInfo[0], currentCategoryInfo[1])
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            messages.error(self.request, "Failed to create expenditure.")
            return render(request, 'partials/bootstrapForm.html', {'form': form})

    def handle_no_permission(self):
        return redirect('logIn')


'''Implements a view for updating an expenditure and handling update expenditure form submissions'''
class UpdateExpenditureView(LoginRequiredMixin, View):

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
            messages.add_message(request, messages.SUCCESS, "Successfully Updated Expenditure")
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Failed to update expenditure - {field}: {error}')
            return redirect(reverse('category', args=[kwargs['categoryId']]))
                                
    
    def handle_no_permission(self):
        return redirect('logIn')


'''Implements a view for deleting an expenditure'''
class DeleteExpenditureView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.get(id=kwargs['expenditureId'])
        # Removing receipt from folder if exists
        receiptPath = os.path.join(settings.MEDIA_ROOT, expenditure.receipt.name)
        if not os.path.isdir(receiptPath):
            os.remove(receiptPath)

        expenditure.delete()
        messages.add_message(request, messages.SUCCESS, "Expenditure successfully deleted")
        return redirect(reverse('category', args=[kwargs['categoryId']]))

    def handle_no_permission(self):
        return redirect('logIn')


class SignUpView(View):
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

            # assign house
            n = user.id % 4
            house=House.objects.get(id=n+1)
            user.house=house
            user.save()
            house.memberCount=house.memberCount+1
            house.save()
            housePointsUpdate(user, 50)
           
            return redirect('home')
        return render(request, 'signUp.html', {'form': signUpForm})


class LogInView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            form = LogInForm()
            return render(request, 'logIn.html', {"form": form})

    def post(self, request, *args, **kwargs):
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.lastLogin.date() != datetime.now().date():
                    # if this is the first login of the day, add 5 points
                    updatePoints(user, 5)
                    createBasicNotification(user, "New Points Earned!", "5 points earned for daily login")
                # Update user lastLogin after checking if this is is first login of the day
                user.lastLogin = timezone.now()
                user.save(update_fields=['lastLogin'])
                return redirect('home')

        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return render(request, 'logIn.html', {"form": form})


class LogOutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('index')

    def handle_no_permission(self):
        return redirect('logIn')


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'index.html')


def generateGraph(categories, spentInCategories, type, graphNum = ''):
    dict = {f'labels{graphNum}': categories, f'data{graphNum}': spentInCategories, f'type{graphNum}':type}
    return dict


'''Implements a view for handling requests to the home page'''
class HomeView(LoginRequiredMixin, View):

    def get(self, request):
        categories = []
        totalSpent = []

        for category in Category.objects.filter(users__in=[request.user]):
            # all categories
            categories.append(str(category))
            # total spend per category
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

    def handle_no_permission(self):
        return redirect('logIn')

'''Implements a view for handling requests to the scores page'''
class ScoresView(LoginRequiredMixin, ListView):
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

    def handle_no_permission(self):
        return redirect('logIn')


class ReportsView(LoginRequiredMixin, View):
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

            # Generate a graph for historical data
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
            
        # Handles what happens if it's false

    def handle_no_permission(self):
        return redirect('logIn')

'''View that handles requests to the profile page'''
class ProfileView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request,'profile.html')

    def handle_no_permission(self):
        return redirect('logIn')


'''View that handles requests to the edit profile page'''
class EditProfileView(LoginRequiredMixin, View):

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


'''Implements a view function for marking notifications as read'''
class EditNotificationsView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        notification = Notification.objects.get(id=kwargs['notificationId'])
        notification.isSeen = not notification.isSeen
        notification.save()

        # Making the user stay on whichever page they called this request
        return redirect(request.META['HTTP_REFERER'])

    def handle_no_permission(self):
        return redirect('logIn')


'''Implements a view function for deleting a notification'''
class DeleteNotificationsView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        notification = Notification.objects.get(id=kwargs['notificationId'])
        if notification.isSeen:
            Notification.objects.get(id=kwargs['notificationId']).delete()
        return redirect("notifications")

    def handle_no_permission(self):
        return redirect('logIn')


'''Implements a view function for deleting all read notifications'''
class DeleteAllNotifications(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        Notification.objects.filter(toUser = request.user, isSeen = True).delete()
        return redirect("notifications")

    def handle_no_permission(self):
        return redirect('logIn')


'''View that shows individual user details.'''
class ShowUserView(LoginRequiredMixin, DetailView):

    model = User
    template_name = 'showUser.html'
    context_object_name = "otherUser"
    pk_url_kwarg = 'userId'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    '''Generate content to be displayed in the template.'''
    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, **kwargs)
        user = self.get_object()
        context['following'] = self.request.user.isFollowing(user)
        context['followable'] = (self.request.user != user)
        return context

    '''Handle get request, and redirect to users if userId invalid.'''
    def get(self, request, *args, **kwargs):

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect(reverse('users'))

    def handle_no_permission(self):
        return redirect('logIn')


'''View that handles follow/unfollow user functionality'''
class FollowToggleView(LoginRequiredMixin, View):

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


'''Implements a view for accepting a follow request category requests'''
class AcceptFollowRequestView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
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

'''View that shows a list of all users and allows user to filter users based on username'''
class UserListView(LoginRequiredMixin, ListView):

    model = User
    template_name = 'users.html'
    context_object_name = 'users'
    paginate_by = 10

    '''Generate content to be displayed in the template.'''
    def get_context_data(self, *args, **kwargs):

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


'''Implements a view for updating or setting the overall spending limit for the user.'''
class SetOverallSpendingLimitView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = OverallSpendingForm(user=request.user)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = OverallSpendingForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully updated overall spending limit.")
            return redirect('home')
        else:
            validationErrors = form.errors.get('__all__', [])
            if validationErrors:
                for error in validationErrors:
                    messages.error(request, error)
            else:
                messages.error(request, 'Failed to update overall spending limit.')
            return redirect('home')

    def handle_no_permission(self):
        return redirect('logIn')
