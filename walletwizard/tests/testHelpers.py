''' File of helper functions used within tests'''
from walletwizard.models import User
from django.contrib.auth.hashers import make_password
from django.urls import reverse

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url

class LogInTester:
    def isUserLoggedIn(self):
        return '_auth_user_id' in self.client.session.keys()

def createUsers(num):
    users = []
    for i in range(num):
        user = User.objects.create(
            username=f"user{i+1}",
            first_name=f"first_name{i+1}",
            last_name=f"last_name{i+1}",
            email=f"user{i+1}@example.com",
            password=make_password("password")
        )
        users.append(user)
    return users

def getNotificationTitles(notifications):
    titles=[]
    for notif in notifications:
        titles.append(notif.title)
    return titles

def getNotificationMessages(notifications):
    messages=[]
    for notif in notifications:
        messages.append(notif.message)
    return messages