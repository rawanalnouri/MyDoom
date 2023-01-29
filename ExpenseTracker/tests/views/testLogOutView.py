from django.test import TestCase
from ExpenseTracker.models import User

class LogOutViewTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        
    def testLogOutView(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/logOut/')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, '/')