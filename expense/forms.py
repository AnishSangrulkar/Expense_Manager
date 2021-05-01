from django import forms
from django.utils import timezone
from django.db.models.functions import datetime
from expense.models import ExpenseList
import datetime

class TimeInput(forms.TimeInput):
    input_type = 'time'
    format = "%H:%M"

class DateInput(forms.DateInput):
    input_type='date'

class AddItemform(forms.ModelForm):
    class Meta:
        model = ExpenseList
        widgets = {'date':DateInput(),'time':TimeInput()}
        fields = ['item','price','date','time','category']

class archiveform(forms.Form):
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())
    choices = (('All','All'),('Groceries and Eatables','Groceries and Eatables'),('Trips and Eating outs','Trips and Eating outs'),('Hobbies/Entertainment','Hobbies/Entertainment'),('Fixed Expenses','Fixed Expenses'),('others','others'))
    select_category = forms.ChoiceField(choices=choices,required=False)
    select_item = forms.CharField(max_length=100,required=False)
    fields=['start_date','end_date','select_category','select_item']

class UpdateForm(forms.ModelForm):
    class Meta:
        model = ExpenseList
        widgets = {'date':DateInput(),'time':TimeInput()}
        fields = ['item','price','date','time','category']

class monthlyfilterform(forms.Form):
    start_date = forms.DateField(widget=DateInput(),required=False)
    end_date = forms.DateField(widget=DateInput(),required=False)
    choices = (('All','All'),('Groceries and Eatables','Groceries and Eatables'),('Trips and Eating outs','Trips and Eating outs'),('Hobbies/Entertainment','Hobbies/Entertainment'),('Fixed Expenses','Fixed Expenses'),('others','others'))
    select_category = forms.ChoiceField(choices=choices,required=False)
    select_item = forms.CharField(max_length=100,required=False)
    fields=['start_date','end_date','select_category','select_item']

class selectmonthform(forms.Form):
    month_ch = ((i,i) for i in range(1,13))
    year_ch = ((i,i) for i in range(2020,datetime.date.today().year+1))
    select_month = forms.ChoiceField(choices=month_ch,required=True)
    select_year = forms.ChoiceField(choices=year_ch,required=True)
    fields=['select_month','select_year']