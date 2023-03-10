from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout
from django.http import Http404
from django.core.paginator import Paginator
from .helpers.pointsHelper import addPoints
from django.utils.timezone import datetime
from .models import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .helpers.pointsHelper import addPoints
from django.utils.timezone import datetime
from .helpers.utils import *
from .notificationContextProcessor import getNotifications
from datetime import datetime

class CategoryView(LoginRequiredMixin, TemplateView):
    '''Displays a specific category and handles create expenditure and edit category form submissions.'''

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
            cur = category.totalSpent() 
            spendingData.append(cur)
            spendingData.append(round(float(category.spendingLimit.amount) - cur, 2))

        graphData = generateGraph(categoryLabels, spendingData, "doughnut")
        context.update(graphData)

        return context

    def handle_no_permission(self):
        return redirect("logIn")
    

class CreateExpenditureView(LoginRequiredMixin, View):
    '''Implements a view for creating expenditures'''

    def get(self, request, *args, **kwargs):
        form = ExpenditureForm()
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = ExpenditureForm(request.POST)
        if category and form.is_valid():
            messages.success(self.request, "Expenditure created successfully.")
            form.save(category)
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            messages.error(self.request, "Failed to create expenditure.")
            return render(request, 'partials/bootstrapForm.html', {'form': form})

    def handle_no_permission(self):
        return redirect('logIn')


class EditCategoryView(LoginRequiredMixin, View):
    '''Implements a view for editing categories'''

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = CategorySpendingLimitForm(user=request.user, instance=category)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = CategorySpendingLimitForm(request.POST, user=request.user, instance=category)
        if category and form.is_valid():
            messages.success(self.request, "Category updated successfully.")
            form.save(category)
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            messages.error(self.request, "Failed to update category.")
            return render(request, 'partials/bootstrapForm.html', {'form': form})

    def handle_no_permission(self):
        return redirect('logIn')


class CategoryCreateView(LoginRequiredMixin, CreateView):
    '''Implements a view for creating a new category using a form'''

    model = Category
    form_class = CategorySpendingLimitForm
    template_name = 'categoryForm.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        category = form.save()
        messages.add_message(self.request, messages.SUCCESS, "Successfully Created Category")
        # add points
        addPoints(self.request,5)
        createBasicNotification(self.request.user, "New Points Earned!", "5 points earned for creating a new category")
        return redirect(reverse('category', args=[category.id]))

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.add_message(self.request, messages.ERROR, error)
        return super().form_invalid(form)
    
    def handle_no_permission(self):
        return redirect('logIn')


class CategoryDeleteView(LoginRequiredMixin, View):
    '''Implements a view for deleting an expenditure'''

    def dispatch(self, request, *args, **kwargs):
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
    

class CategoryShareView(LoginRequiredMixin, View):
    '''Implements a view for sharing categories'''

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
            messages.add_message(request, messages.ERROR, "Failed to send share category request ")
            return render(request, 'partials/bootstrapForm.html', {'form': form})

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
    
    
class ExpenditureUpdateView(LoginRequiredMixin, View):
    '''Implements a view for updating an expenditure and handling update expenditure form submissions'''

    def get(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.filter(id=kwargs['expenditureId']).first()
        form = ExpenditureForm(instance=expenditure)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.filter(id=kwargs['expenditureId']).first()
        form = ExpenditureForm(instance=expenditure, data=request.POST)
        if form.is_valid():
            category = Category.objects.get(id=kwargs['categoryId'])
            form.save(category)
            messages.add_message(request, messages.SUCCESS, "Successfully Updated Expenditure")
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            messages.add_message(request, messages.ERROR, "Failed to Update Expenditure")
            return render(request, 'partials/bootstrapForm.html', {'form': form})
    
    def handle_no_permission(self):
        return redirect('logIn')


class ExpenditureDeleteView(LoginRequiredMixin, View):
    '''Implements a view for deleting an expenditure'''

    def dispatch(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.get(id=kwargs['expenditureId'])
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
            pointsObject = Points()
            pointsObject.user=user
            pointsObject.pointsNum=50
            pointsObject.save()
    
            login(request, user)
            createBasicNotification(self.request.user, "New Points Earned!", str(pointsObject.pointsNum) + " points earned for signing up!")
            createBasicNotification(self.request.user, "Welcome to spending trracker!", "Manage your money here and earn points for staying on track!")

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

                if user.last_login.date() != datetime.now().date():
                    # if this is the first login of the day, add 5 points
                    addPoints(request, 5)
                    createBasicNotification(self.request.user, "New Points Earned!", "5 points earned daily login")


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


def generateGraph(categories, spentInCategories, type):
    dict = {'labels': categories, 'data': spentInCategories, 'type':type}
    return dict


class HomeView(LoginRequiredMixin, View):
    '''Implements a view for handling requests to the home page'''

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

        context = {**generateGraph(categories, totalSpent,'pie'), **{
            'month': datetime.now().strftime('%B'),
            'year': datetime.now().strftime('%Y'),
            'points': Points.objects.get(user=request.user).pointsNum,
        }}

        return render(request, "home.html", context)
    
    def handle_no_permission(self):
        return redirect('logIn')
    

def reportsView(request):
    '''Implements a view for handling requests to the reports page'''

    categories = []
    totalSpent = []

    if request.method == 'POST':
        form = ReportForm(request.POST, user=request.user)
        if form.is_valid():
            timePeriod = form.cleaned_data.get('timePeriod')
            selectedCategory = form.cleaned_data.get('selectedCategory')
            for selected in selectedCategory:
                category = Category.objects.get(name=selected)
                # all categories
                categories.append(selected)
                # total spend per catagory
                categorySpend = 0.00
                for expence in category.expenditures.all():
                    categorySpend += float(expence.amount)
                totalSpent.append(categorySpend/float(category.spendingLimit.getNumber())*100)

            dict = generateGraph(categories, totalSpent, 'bar')
            dict.update({"form": form})

            return render(request, "reports.html", dict)

    form = ReportForm(user=request.user)
    dict = generateGraph(categories, totalSpent, 'bar')
    dict.update({"form": form})
    return render(request, "reports.html", dict)

    # def get(self, request):
    #     categories = []
    #     totalSpent = []
    #     for category in Category.objects.filter(user=self.request.user):
    #         # all categories
    #         categories.append(str(category))
    #         # total spend per catagory
    #         categorySpend = 0.00
    #         for expence in category.expenditures.all():
    #             categorySpend += float(expence.amount)
    #         totalSpent.append(categorySpend/float(category.spendingLimit.getNumber())*100)
    #
    #     return render(request, "reports.html", generateGraph(categories, totalSpent, 'bar'))
    #
    #     return render(request, 'reports.html', generateGraph(["a","b","c"], [1,1,2], 'polarArea'))


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