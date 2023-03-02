''' File of helper functions used within tests'''

class LogInTester:
    def isUserLoggedIn(self):
        return '_auth_user_id' in self.client.session.keys()

