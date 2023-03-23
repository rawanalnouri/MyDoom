"""Views for user profile."""
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from walletwizard.forms import EditProfileForm, PasswordChangeForm, OverallSpendingForm


class ProfileView(LoginRequiredMixin, View):
    '''View to display logged-in user's profile.'''

    def get(self, request):
        return render(request,'profile.html')


class EditProfileView(LoginRequiredMixin, View):
    '''View to edit logged-in user's profile.'''

    def get(self,request):
        form = EditProfileForm(instance=request.user)
        return render(request, "editProfile.html", {'form': form})

    def post(self,request):
        form = EditProfileForm(instance=request.user, data=request.POST)
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


class SetOverallSpendingLimitView(LoginRequiredMixin, View):
    '''View to update or set the logged-in user's overall spending limit.'''

    def get(self, request, *args, **kwargs):
        spendingLimit = request.user.overallSpendingLimit
        form = OverallSpendingForm(
            user = request.user, 
            initial = {
                'timePeriod': spendingLimit.timePeriod, 
                'amount': spendingLimit.amount
            }
        )
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