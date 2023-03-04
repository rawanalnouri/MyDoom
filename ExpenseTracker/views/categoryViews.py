from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from ExpenseTracker.models import *
from ExpenseTracker.forms import *
from .helpers import addPoints, generateGraph

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
        return redirect(reverse('category', args=[category.id]))

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.add_message(self.request, messages.ERROR, error)
        return super().form_invalid(form)
    
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