from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required 
import datetime
from expense.models import ExpenseList
from django.contrib.auth.models import User
from expense.forms import AddItemform,UpdateForm,monthlyfilterform,archiveform,selectmonthform
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Sum
from django.http import JsonResponse
from calendar import monthrange

def home(request):
    return render(request,'expense/home.html')

@login_required
def dashboard(request):
    if request.method == 'POST':
        form = AddItemform(request.POST)
        if(form.is_valid()):
            form.instance.author = request.user
            form.save()
            messages.success(request, f'Item has been added to the list..!')
            return redirect('dashboard')
    else:
        form = AddItemform()
    d2 = datetime.datetime.today()
    ttoday=0
    tweek=0
    for element in request.user.expenselist_set.all():
        if element.date == datetime.datetime.today().date():
            ttoday+=element.price
        if element.date.isocalendar()[1] == d2.isocalendar()[1] and element.date.year == d2.year:
            tweek+=element.price
    
    context = {'groceries':request.user.expenselist_set.filter(category='Groceries and Eatables').all().order_by('-date','-time'),
                'trip':request.user.expenselist_set.filter(category='Trips and Eating outs').all().order_by('-date','-time'),
                'fixed':request.user.expenselist_set.filter(category='Fixed Expenses').all().order_by('-date','-time'),
                'others':request.user.expenselist_set.filter(category='others').all().order_by('-date','-time'),
                'ent': request.user.expenselist_set.filter(category='Hobbies/Entertainment').all().order_by('-date','-time'),
                'form':form,'todays':ttoday,'weeks':tweek
              }
    return render(request,'expense/dashboard.html',context)

@login_required
def archive(request):
    context = {}
    total_spend=0
    if request.method == 'POST':
        form = archiveform(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            select_cat = form.cleaned_data.get('select_category')
            select_item = form.cleaned_data.get('select_item')
            context['start_date'] = start_date
            context['end_date'] = end_date
            context['select_category']=select_cat
            context['select_item']=select_item
            if select_cat=='All':
                if select_item:
                    filt_list = request.user.expenselist_set.filter(date__range = [start_date,end_date],item = select_item).all().order_by('-date','-time')
                    for element in filt_list:
                        total_spend+=element.price
                    context['total_spend']=total_spend
                    context['filter_list'] = filt_list
                else :
                    filt_list = request.user.expenselist_set.filter(date__range = [start_date,end_date]).all().order_by('-date','-time')
                    for element in filt_list:
                        total_spend+=element.price
                    context['total_spend']=total_spend
                    context['filter_list'] = filt_list
            else :
                if select_item:
                    filt_list = request.user.expenselist_set.filter(date__range = [start_date,end_date],category=select_cat,item = select_item).all().order_by('-date','-time')
                    for element in filt_list:
                        total_spend+=element.price
                    context['total_spend']=total_spend
                    context['filter_list'] = filt_list
                else :
                    filt_list = request.user.expenselist_set.filter(date__range = [start_date,end_date],category=select_cat).all().order_by('-date','-time')
                    for element in filt_list:
                        total_spend+=element.price
                    context['total_spend'] = total_spend
                    context['filter_list'] = filt_list
        context['category_pie']=arch_categorypie(request.user,start_date,end_date)
        context['weekday_bar']=arch_weekdaybar(request.user,start_date,end_date)
    else :
        form = archiveform(initial={'select_category':'All','select_item':None})
    context['form']=form
    return render(request,'expense/archive.html',context)

def arch_categorypie(user,start_date,end_date):
    queryset = user.expenselist_set.filter(date__range = [start_date,end_date]).order_by('date')
    labels = []
    value = []
    dict = {}
    for entry in queryset:
        if entry.category in dict:
            dict[entry.category]+=entry.price
        else :
            dict[entry.category]=entry.price
    for key,val in dict.items():
        labels.append(key)
        value.append(val)
    return {'labels':labels,'value':value}

def arch_weekdaybar(user,start_date,end_date):
    queryset = user.expenselist_set.filter(date__range=[start_date,end_date]).all()
    labels = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    dict = {'Monday':0,'Tuesday':0,'Wednesday':0,'Thursday':0,'Friday':0,'Saturday':0,'Sunday':0}
    for entry in queryset:
        d = entry.date.strftime('%A')
        dict[d]+=entry.price
    value = []
    for l in labels:
        value.append(dict[l])
    return {'labels':labels,'value':value}

@login_required
def update(request,pk):
    if request.method == 'POST':
        if 'delete' in request.POST:
            exp = request.user.expenselist_set.get(pk=pk)
            exp.delete()
            messages.warning(request,'Selected item has been deleted permenantly..!')
            return HttpResponseRedirect(request.session['pre_url'])
        form = UpdateForm(request.POST)
        if form.is_valid():
            if 'edit' in request.POST:
                exp = request.user.expenselist_set.get(pk=pk)
                exp.item = form.cleaned_data.get('item')
                exp.price = form.cleaned_data.get('price')
                exp.time = form.cleaned_data.get('time')
                exp.date = form.cleaned_data.get('date')
                exp.category = form.cleaned_data.get('category')
                exp.save()
                messages.success(request,'Selected item has been updated..!')
                return HttpResponseRedirect(request.session['pre_url'])
    else:
        request.session['pre_url'] = request.META.get('HTTP_REFERER', '/')
        exp = request.user.expenselist_set.get(pk=pk)
        initial = {'item':exp.item,'price':exp.price,'date':exp.date,'time':exp.time,'category':exp.category}
        form = UpdateForm(initial=initial)
        return render(request,'expense/update.html',{'form':form})

@login_required
def delete(request,pk):
    exp = request.user.expenselist_set.get(pk=pk)
    exp.delete()
    messages.warning(request,'Selected item has been deleted permenantly..!')
    return redirect('dashboard')

@login_required
def select_month(request):
    if request.method=='POST':
        form = selectmonthform(request.POST)
        if form.is_valid():
            request.session['month'] = form.cleaned_data.get('select_month')
            request.session['year']=form.cleaned_data.get('select_year')
    return redirect('monthly_analysis')

@login_required
def monthly_analysis(request):
    context = {}
    if 'month' not in request.session:
        context['today']=datetime.date.today()
        month = datetime.date.today().month
        year = datetime.date.today().year
        request.session['day'] = datetime.date.today().day
        
    else :
        month = int(request.session['month'])
        year = int(request.session['year'])
        context['today']=datetime.datetime(year,month,monthrange(year,month)[1])
        request.session['day'] = context['today'].day
    request.session['month'] = month
    request.session['year'] = year
    form2=selectmonthform(initial={'select_month':month,'select_year':year})
    context['form2']=form2
    total_spend = 0
    if request.method == 'POST':
        form = monthlyfilterform(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            select_cat = form.cleaned_data.get('select_category')
            select_item = form.cleaned_data.get('select_item')
            if select_cat=='All':
                if select_item:
                    filt_list = request.user.expenselist_set.filter(date__range = [start_date,end_date],item = select_item).all().order_by('-date','-time')
                    for element in filt_list:
                        total_spend+=element.price
                    context['total_spend']=total_spend
                    context['filter_list'] = filt_list
                else :
                    filt_list = request.user.expenselist_set.filter(date__range = [start_date,end_date]).all().order_by('-date','-time')
                    for element in filt_list:
                        total_spend+=element.price
                    context['total_spend']=total_spend
                    context['filter_list'] = filt_list
            else :
                if select_item:
                    filt_list = request.user.expenselist_set.filter(date__range = [start_date,end_date],category=select_cat,item = select_item).all().order_by('-date','-time')
                    for element in filt_list:
                        total_spend+=element.price
                    context['total_spend']=total_spend
                    context['filter_list'] = filt_list
                else :
                    filt_list = request.user.expenselist_set.filter(date__range = [start_date,end_date],category=select_cat).all().order_by('-date','-time')
                    for element in filt_list:
                        total_spend+=element.price
                    context['total_spend'] = total_spend
                    context['filter_list'] = filt_list
    else:
        form = monthlyfilterform(initial={'start_date':datetime.datetime(year,month,1),'end_date':context['today'],'select_category':'All','select_item':None})
        filt_list = request.user.expenselist_set.filter(date__month = month).all().order_by('-date','-time')
        context['filter_list']=filt_list
        for element in filt_list:
            total_spend+=element.price
        context['total_spend'] = total_spend
    context['form'] = form
    cat_pie = category_pie(request)
    context['category_pie_labels'] = cat_pie['labels']
    context['category_pie_value'] = cat_pie['value']
    context['compare_bar'] = compare_bar(request)
    context['weekday_bar'] = weekday_bar(request)
    return render(request,'expense/monthly_analysis.html',context=context)

def date_vs_expense(request):
    labels = []
    amount = []
    dict = {}
    queryset = request.user.expenselist_set.filter(date__month = int(request.session['month']),date__year = int(request.session['year'])).order_by('date')
    for entry in queryset:
        if entry.date.day in dict:
            dict[entry.date.day]+=entry.price
        else :
            dict[entry.date.day] = entry.price
    labels = [x for x in range(1,int(request.session['day'])+1)]
    amount = []
    for l in labels:
        if l in dict:
            amount.append(dict[l])
        else:
            amount.append(0)
    return JsonResponse(data={'labels':labels,'amount':amount})

def category_pie(request):
    queryset = request.user.expenselist_set.filter(date__month=int(request.session['month']),date__year = int(request.session['year'])).order_by('date')
    labels = []
    value = []
    dict = {}
    for entry in queryset:
        if entry.category in dict:
            dict[entry.category]+=entry.price
        else :
            dict[entry.category]=entry.price
    for key,val in dict.items():
        labels.append(key)
        value.append(val)
    return {'labels':labels,'value':value}

def compare_bar(request):
    today = datetime.datetime(int(request.session['year']),int(request.session['month']),int(request.session['day']))
    this = request.user.expenselist_set.filter(date__month = (today.month)).all()
    year = today.year if today.month>1 else today.year-1
    month = today.month-1 if today.month>1 else 12
    date = min(today.day,monthrange(year,month)[1])
    last = request.user.expenselist_set.filter(date__range = [datetime.datetime(year,month,1),datetime.datetime(year,month,date)]).all()
    labels = ['All','Groceries and Eatables','Trips and Eating outs','Hobbies/Entertainment','Fixed Expenses','others']
    curr={'All':0,'Groceries and Eatables':0,'Trips and Eating outs':0,'Hobbies/Entertainment':0,'Fixed Expenses':0,'others':0}
    pre={'All':0,'Groceries and Eatables':0,'Trips and Eating outs':0,'Hobbies/Entertainment':0,'Fixed Expenses':0,'others':0}
    total1 = 0
    total2 = 0
    for entry in this:
        curr[entry.category]+=entry.price
        total1+=entry.price
    for entry in last:
        pre[entry.category]+=entry.price
        total2+=entry.price
    value1 = []
    value2 = []
    value1.append(total1)
    value2.append(total2)
    for l in labels:
        if l!='All':
            value1.append(curr[l])
            value2.append(pre[l])
    return {'labels':labels,'value1':value1,'value2':value2}

def weekday_bar(request):
    queryset = request.user.expenselist_set.filter(date__month=int(request.session['month']),date__year = int(request.session['year'])).all()
    labels = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    dict = {'Monday':0,'Tuesday':0,'Wednesday':0,'Thursday':0,'Friday':0,'Saturday':0,'Sunday':0}
    for entry in queryset:
        d = entry.date.strftime('%A')
        dict[d]+=entry.price
    value = []
    for l in labels:
        value.append(dict[l])
    return {'labels':labels,'value':value}