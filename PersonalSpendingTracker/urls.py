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
from django.urls import path
from ExpenseTracker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('reports/', ReportsView.as_view(), name='reports'),
    path('create_category/', CategoryCreateView.as_view(), name='create_category'),
    path('category/<str:category_name>/', CategoryView.as_view(), name='category')


    path("", views.homePage, name="homePage"),
    path("signUp/",views.signUp, name="signUp" ),
    path("logIn/",views.logIn, name="logIn"),
    path("logOut/",views.logOut, name="logOut"),

    path("landingPage/<int:user_id>/", views.landingPage, name="landingPage")
]
