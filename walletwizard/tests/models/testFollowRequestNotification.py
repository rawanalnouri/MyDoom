'''Additional unit tests for the Follow Request Notification model.'''
from walletwizard.models import FollowRequestNotification, User
from django.test import TestCase
from django.core.exceptions import ValidationError

class FollowRequestNotificationModelTestCase(TestCase):
    '''Additional unit tests for the Follow Request Notification model.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.notification = FollowRequestNotification.objects.get(id=4)
    
    def _assertNotificationIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testFromUserCannotBeBlank(self):
        self.notification.fromUser = None
        self._assertNotificationIsInvalid()

    def testFromUserInNotificationExistsInUsers(self):
        notificationFromUser = self.notification.fromUser
        self.assertTrue(User.objects.filter(id=notificationFromUser.id).exists())