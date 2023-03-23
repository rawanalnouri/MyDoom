'''Unit tests for the Notification model.'''
from walletwizard.models import Notification, User, ShareCategoryNotification, FollowRequestNotification, Category
from django.test import TestCase
from django.core.exceptions import ValidationError

class NotificationModelTestCase(TestCase):
    '''Unit tests for the Notification model.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.notification = Notification.objects.get(id=1)
    
    def testToUserCannotBeNone(self):
        self.notification.toUser = None
        self._assertNotificationIsInvalid()

    def testToUserInNotificationExistsInUsers(self):
        notificationToUser = self.notification.toUser
        self.assertTrue(User.objects.filter(id=notificationToUser.id).exists())
    
    def testTitleCannotBeEmpty(self):
        self.notification.title = ''
        self._assertNotificationIsInvalid()

    def testTitleCannotBeNone(self):
        self.notification.toUser = None
        self._assertNotificationIsInvalid()

    def testTitleMustBeAtMostEightyCharactersLong(self):
        self.notification.title = 'x' * 81
        self._assertNotificationIsInvalid()
    
    def testTitleCanBeEightyCharactersLong(self):
        self.notification.title = 'x' * 80
        self._assertNotificationIsValid()
    
    def testMessageCannotBeEmpty(self):
        self.notification.message = ''
        self._assertNotificationIsInvalid()

    def testMessageCannotBeNone(self):
        self.notification.message = None
        self._assertNotificationIsInvalid()
    
    def testMessageMustBeAtMostTwoHundredAndFiftyCharactersLong(self):
        self.notification.message = 'x' * 251
        self._assertNotificationIsInvalid()
    
    def testMessageCanBeTwoHundredAndFiftyCharactersLong(self):
        self.notification.message = 'x' * 250
        self._assertNotificationIsValid()
    
    def testIsSeenFieldCanBeFalse(self):
        self.notification.isSeen = 0
        self._assertNotificationIsValid()

    def testIsSeenFieldCanBeTrue(self):
        self.notification.isSeen = 0
        self._assertNotificationIsValid()

    def testIsSeenFieldMustBeValid(self):
        self.notification.isSeen = 4
        self._assertNotificationIsInvalid()

    def testTypeChoicesCanBe(self):
        self.notification.isSeen = 4
        self._assertNotificationIsInvalid()

    def testInvalidTypeChoice(self):
        self.notification.type = 'invalidChoice'
        self._assertNotificationIsInvalid()

    def testTypeMustBeFromNotificationTypeChoices(self):
        for choice in Notification.TYPE_CHOICES:
            self.notification.type = choice[0]
            self._assertNotificationIsValid()
    
    def testNotificationToStringIsEqualToMessage(self):
        self.assertEqual(self.notification.message, str(self.notification))

    def _assertNotificationIsValid(self):
        try:
            self.notification.full_clean()
        except:
            self.fail('Test notification should be valid')
    
    def _assertNotificationIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.notification.full_clean()