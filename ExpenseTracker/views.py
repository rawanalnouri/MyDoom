from django.shortcuts import render, redirect, reverse
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout
from .forms import SignUpForm, LogInForm
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
from .contextProcessor import getNotifications
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
            'expenditureForm': ExpenditureForm(),
            'categoryForm': CategorySpendingLimitForm(user=self.request.user, instance=category),
            'expenditures': expenditures,
        }

        categories = []
        totalSpent = []
        categorySpend = 0
        for category in Category.objects.filter(id=kwargs["categoryId"], users__in=[self.request.user]):
            categories.append(str(category))
            categories.append("Remaining Budget")
            # total spend per category
            categorySpend = 0.0
            for expense in category.expenditures.all():
                categorySpend += float(expense.amount)
            totalSpent.append(categorySpend)
            totalSpent.append(float(category.spendingLimit.getNumber()) - categorySpend)

        graphData = generateGraph(categories, totalSpent, "doughnut")
        context.update(graphData)

        # analysis
        namesOfExpenses = []
        allExpensesInRange = category.expenditures.all().filter(date__year="2023", date__month="01")
        # filter between months
        # Sample.objects.filter(date__range=["2011-01-01", "2011-01-31"])
        for expense in allExpensesInRange:
            namesOfExpenses.append(expense.title)

        context.update({'stuff': namesOfExpenses})
        return context

    def handleForm(self, form, category, error_message, success_message):
        if category and form.is_valid():
            messages.success(self.request, success_message)
            form.save(category)
        else:
            messages.error(self.request, error_message)

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs["categoryId"])
        expForm = ExpenditureForm(request.POST)
        catForm = CategorySpendingLimitForm(request.POST, user=request.user, instance=category)

        if "expenditureForm" in request.POST:
            self.handleForm(expForm, category, "Failed to create expenditure.","Expenditure created successfully.")

        elif "categoryForm" in request.POST:
            self.handleForm(catForm, category, "Failed to update category.", "Category updated successfully.")

        # using hidden id to modal templates to determine which form is being used
        context = {"expenditureForm": expForm, "categoryForm": catForm}
        return redirect(reverse("category", args=[category.id]), context=context)

    def handle_no_permission(self):
        return redirect("login")


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
        form = ShareCategoryForm(user=request.user, category=category)
        return render(request, 'partials/bootstrapForm.html', {'form': form})

    def post(self, request, *args, **kwargs):
        category = Category.objects.get(id=kwargs['categoryId'])
        form = ShareCategoryForm(user=request.user, category=category, data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully Added New User to Category")
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            messages.add_message(request, messages.ERROR, "Failed to Add User to Category")
            return render(request, 'partials/bootstrapForm.html', {'form': form})

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
            return redirect('home')
        return render(request, 'signUp.html', {'form': signUpForm})


class LogInView(View):
    def get(self, request, *args, **kwargs):
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

                if request.user.last_login.date() != datetime.now().date():
                    # check if it is the users first time logging in that day, only add points if this is their first login of the day 
                    addPoints(request,5)


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
            # total spend per catagory
            categorySpend = 0.00
            for expence in category.expenditures.all():
                categorySpend += float(expence.amount)
            totalSpent.append(categorySpend/float(category.spendingLimit.getNumber())*100)

        return render(request, "home.html", generateGraph(categories, totalSpent, 'polarArea'))
    
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


class ShowUserView(LoginRequiredMixin, DetailView):
    """View that shows individual user details."""

    model = User
    template_name = 'showUser.html'
    context_object_name = "user"
    pk_url_kwarg = 'user_id'

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
        """Handle get request, and redirect to users if user_id invalid."""

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
            currentUser.toggleFollow(followee)
        except ObjectDoesNotExist:
            return redirect('users')
        else:
            return redirect('showUser', user_id=userId)
    
    def handle_no_permission(self):
        return redirect('logIn')


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


class ChangePassword(LoginRequiredMixin, PasswordChangeView, View):
    '''View that changes the user's password'''

    form_class = ChangePasswordForm
    success_url = reverse_lazy('home')

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

class deleteNotificationsView(LoginRequiredMixin, View):
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
        Notification.objects.filter(user = request.user, isSeen = True).delete()
        return redirect("notifications")  
    
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


class ShowUserView(LoginRequiredMixin, DetailView):
    """View that shows individual user details."""

    model = User
    template_name = 'showUser.html'
    context_object_name = "otherUser"
    pk_url_kwarg = 'user_id'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""

        context = super().get_context_data(*args, **kwargs)
        otherUser = self.get_object()
        context['following'] = self.request.user.isFollowing(otherUser)
        context['followable'] = (self.request.user != otherUser)
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to users if user_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect(reverse('users'))

    def handle_no_permission(self):
        return redirect('logIn')


class FollowToggleView(LoginRequiredMixin, View):
    '''View that handles follow/unfollow user functionality'''

    def get(self, request, userId, *args, **kwargs):
        try:
            followee = User.objects.get(id=userId)
            request.user.toggleFollow(followee)
        except ObjectDoesNotExist:
            return redirect('users')
        else:
            # Redirect to the previous page or URL
            return redirect(request.META.get('HTTP_REFERER', 'users'))
    
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
