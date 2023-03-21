"""Views that relate to expenditures."""
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from PersonalSpendingTracker import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from walletwizard.models import Category, Expenditure
from walletwizard.forms import ExpenditureForm
import os
from walletwizard.helpers.pointsHelpers import trackPoints, checkIfOver

        
class CreateExpenditureView(LoginRequiredMixin, View):
    '''View that creates an expenditure for the logged-in user.'''

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


class EditExpenditureView(LoginRequiredMixin, View):
    '''View that updates an expenditure of the logged-in user.'''

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