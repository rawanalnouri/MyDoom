from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from ExpenseTracker.models import *
from ExpenseTracker.forms import *


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
    

class UpdateExpenditureView(LoginRequiredMixin, View):
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


class DeleteExpenditureView(LoginRequiredMixin, View):
    '''Implements a view for deleting an expenditure'''

    def dispatch(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.get(id=kwargs['expenditureId'])
        expenditure.delete()
        messages.add_message(request, messages.SUCCESS, "Expenditure successfully deleted")
        return redirect(reverse('category', args=[kwargs['categoryId']]))
    
    def handle_no_permission(self):
        return redirect('logIn')