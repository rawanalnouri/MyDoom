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
from ExpenseTracker.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path("signUp/", SignUpView.as_view(), name="signUp" ),
    path("logIn/", LogInView.as_view(), name="logIn"),
    path("logOut/",LogOutView.as_view(), name="logOut"),

    path('home/', HomeView.as_view(), name='home'),
    path('', IndexView.as_view(), name='index'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('deleteAllNotifications/', DeleteAllNotifications.as_view(), name='deleteAllNotifications'),
    path('deleteNotifcations/<int:notificationId>/', DeleteNotificationsView.as_view(), name='deleteNotifications'),
    path('editnotifcations/<int:notificationId>/', EditNotificationsView.as_view(), name='editNotifications'),
    path('declineRequest/<int:notificationId>', DeclineRequestView.as_view(), name='declineRequest'),
    path('acceptCategoryShareView/<int:notificationId>', AcceptCategoryShareView.as_view(), name='acceptCategoryShare'),
    path('acceptFollowRequest/<int:notificationId>/', AcceptFollowRequestView.as_view(), name='acceptFollowRequest'),

    path('reports/', reportsView, name='reports'),
    path('createCategory/', CategoryCreateView.as_view(), name='createCategory'),
    path('deleteCategory/<int:categoryId>/', CategoryDeleteView.as_view(), name='deleteCategory'),
    path('shareCategory/<int:categoryId>/', CategoryShareView.as_view(), name='shareCategory'),
    path('editCategory/<int:categoryId>/', EditCategoryView.as_view(), name='editCategory'),
    path('category/<int:categoryId>/', CategoryView.as_view(), name='category'),

    path('createExpenditure/<int:categoryId>/', CreateExpenditureView.as_view(), name='createExpenditure'),
    path('category/<int:categoryId>/update/<int:expenditureId>/', ExpenditureUpdateView.as_view(), name='updateExpenditure'),
    path('category/<int:categoryId>/delete/<int:expenditureId>/', ExpenditureDeleteView.as_view(), name='deleteExpenditure'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('editProfile/', EditProfileView.as_view(), name='editProfile'),
    path('changePassword/', ChangePasswordView.as_view(template_name = 'changePassword.html'), name='changePassword'),

    path('user/<int:userId>/', ShowUserView.as_view(), name='showUser'),
    path('users/', UserListView.as_view(), name='users'),
    path('followToggle/<int:userId>/', FollowToggleView.as_view(), name='followToggle'),
    path('searchUsers/', searchUsers, name='searchUsers'),
]

# Hanlding adding urls for user added media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)