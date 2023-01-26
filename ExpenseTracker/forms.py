from django import forms
from .models import Category, SpendingLimit

class CategorySpendingLimitForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description']
        widgets = {
            'spending_limit': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CategorySpendingLimitForm, self).__init__(*args, **kwargs)

    start_date = forms.DateField(label="Start date [Day-Month-Year]", input_formats=['%d-%m-%Y'], 
                                 widget=forms.DateInput(format='%d-%m-%Y'))
    end_date = forms.DateField(label="End date [Day-Month-Year]", input_formats=['%d-%m-%Y'], 
                                 widget=forms.DateInput(format='%d-%m-%Y'))
    amount = forms.DecimalField(label="Amount [GBP]", min_value=0.01)

    def save(self, commit=True):
        category = super().save(commit=False)
        spending_limit = SpendingLimit.objects.create(start_date=self.cleaned_data['start_date'],
                                                     end_date=self.cleaned_data['end_date'],
                                                     amount=self.cleaned_data['amount'])
        category.spending_limit = spending_limit
        if commit:
            spending_limit.save()
            category.save()
            self.user.categories.add(category)
        return category