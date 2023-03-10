from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from ExpenseTracker.models import *
from ExpenseTracker.forms import *
from ExpenseTracker.helpers.pointsHelper import addPoints
from .helpers import generateGraph


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


class CreateCategoryView(LoginRequiredMixin, CreateView):
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

class DeleteCategoryView(LoginRequiredMixin, View):
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
    

class ShareCategoryView(LoginRequiredMixin, View):
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