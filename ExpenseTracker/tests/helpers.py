''' File of helper functions used within tests'''
from ExpenseTracker.models import User
from django.contrib.auth.hashers import make_password

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