"""Views that relate to categories."""
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from walletwizard.models import Category
from walletwizard.forms import CategorySpendingLimitForm, ShareCategoryForm
from walletwizard.helpers.pointsHelpers import updatePoints, createBasicNotification
from .helpers import generateGraph


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