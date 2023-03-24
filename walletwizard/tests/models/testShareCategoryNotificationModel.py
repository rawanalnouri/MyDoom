'''Additional unit tests for the Share Category Notification model.'''
from walletwizard.models import ShareCategoryNotification, User, Category
from django.test import TestCase
from django.core.exceptions import ValidationError

class ShareCategoryNotificationModelTestCase(TestCase):
    '''Additional unit tests for the Share Category Notification model.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.notification = ShareCategoryNotification.objects.get(id=3)

    def _assertNotificationIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testFromUserCannotBeBlank(self):
        self.notification.fromUser = None
        self._assertNotificationIsInvalid()

    def testFromUserInNotificationExistsInUsers(self):
        notificationFromUser = self.notification.fromUser
        self.assertTrue(User.objects.filter(id=notificationFromUser.id).exists())

    def testSharedCategoryCannotBeNone(self):
        self.notification.sharedCategory = None
        self._assertNotificationIsInvalid()
    
    def testSharedCategoryInNotificationExistsInCategories(self):
        notificationSharedCategory = self.notification.sharedCategory
        self.assertTrue(Category.objects.filter(id=notificationSharedCategory.id).exists())