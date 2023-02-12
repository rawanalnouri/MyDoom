"""PersonalSpendingTracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path
from ExpenseTracker import views
from ExpenseTracker.views import HomeView, ReportsView, CategoryCreateView, CategoryView, IndexView, EditProfileView, ProfileView, ChangePassword


urlpatterns = [
    path('admin/', admin.site.urls),

    path("signUp/",views.signUp, name="signUp" ),
    path("logIn/",views.logIn, name="logIn"),
    path("logOut/",views.logOut, name="logOut"),


    path('home/', HomeView.as_view(), name='home'),
    path('', IndexView.as_view(), name='index'),

    path('reports/', ReportsView.as_view(), name='reports'),
    path('createCategory/', CategoryCreateView.as_view(), name='createCategory'),
    path('category/<str:categoryName>/', CategoryView.as_view(), name='category'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('editProfile/', EditProfileView.as_view(), name='editProfile'),
    path('changePassword/', ChangePassword.as_view(template_name = 'changePassword.html')),
]

