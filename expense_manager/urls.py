"""expense_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from expense import views as exp_views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',exp_views.home,name='home'),
    path('register/',user_views.register,name='register'),
    path('login/',auth_views.LoginView.as_view(template_name = 'users/login.html'),name = 'login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='users/logout.html'),name='logout'),
    path('dashboard/',exp_views.dashboard,name='dashboard'),
    path('archive/',exp_views.archive,name='archive'),
    path('update/<int:pk>/',exp_views.update,name='update'),
    path('delete/<int:pk>/',exp_views.delete,name='delete'),
    path('monthly_analysis/',exp_views.monthly_analysis,name = 'monthly_analysis'),
    path('date_vs_expense/',exp_views.date_vs_expense,name='date_vs_expense'),
    path('category_pie/',exp_views.category_pie,name='category_pie'),
    path('select_month/',exp_views.select_month,name='select_month'),
]
