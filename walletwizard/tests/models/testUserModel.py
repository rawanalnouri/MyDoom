'''Unit tests for the User model.'''
from walletwizard.models import User, Category, SpendingLimit
from django.test import TestCase
from django.core.exceptions import ValidationError

class UserModelTestCase(TestCase):
    '''Unit tests for the User model.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.secondUser = User.objects.create_user(
            username='janedoe', 
            email='janedoe@example.org', 
            firstName='Jane',
            lastName='Doe',
            password='Password123',
        )

    def _assertUserIsValid(self):
        try:
            self.user.full_clean()
        except:
            self.fail('Test user should be valid')

    def _assertUserIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()


    def testUsernameCannotBeBlank(self):
        self.user.username = ''
        self._assertUserIsInvalid()

    def testUsernameCannotBeNone(self):
        self.user.username = None
        self._assertUserIsInvalid()

    def testUsernameCanBe30CharactersLong(self):
        self.user.username = 'x' * 30
        self._assertUserIsValid()

    def testUsernameMustNotBeOver30CharactersLong(self):
        self.user.username = 'x' * 31
        self._assertUserIsInvalid()

    def testUsernameMustBeUnique(self):
        self.user.username = self.secondUser.username
        self._assertUserIsInvalid()

    def testUsernameMustOnlyContainAlphanumericals(self):
        self.user.username = 'john!doe'
        self._assertUserIsInvalid()

    def testUsernameContainAtLeast3Alphanumericals(self):
        self.user.username = 'jo'
        self._assertUserIsInvalid()

    def testUsernameCanContainNumbers(self):
        self.user.username = 'j0hndoe2'
        self._assertUserIsValid()


    def testFirstNameMustNotBeBlank(self):
        self.user.firstName = ''
        self._assertUserIsInvalid()

    def testFirstNameMustNotBeNone(self):
        self.user.firstName = None
        self._assertUserIsInvalid()

    def testFirstNameMustNotBeOver50CharactersLong(self):
        self.user.firstName = 'x' * 51
        self._assertUserIsInvalid()

    def testFirstNameCanBe50CharactersLong(self):
        self.user.firstName = 'x' * 50
        self._assertUserIsValid()
    

    def testLastNameMustNotBeBlank(self):
        self.user.lastName = ''
        self._assertUserIsInvalid()
    
    def testLastNameMustNotBeNone(self):
        self.user.lastName = None
        self._assertUserIsInvalid()

    def testLastNameMustNotBeOver50CharactersLong(self):
        self.user.lastName = 'x' * 51
        self._assertUserIsInvalid()

    def testLastNameCanBe50CharactersLong(self):
        self.user.firstName = 'x' * 50
        self._assertUserIsValid()


    def testEmailMustNotBeBlank(self):
        self.user.email = ''
        self._assertUserIsInvalid()
    
    def testEmailMustNotBeNone(self):
        self.user.email = None
        self._assertUserIsInvalid()

    def testEmailMustBeUnique(self):
        self.user.email = self.secondUser.email
        self._assertUserIsInvalid()

    def testEmailMustContainUsername(self):
        self.user.email = '@example.org'
        self._assertUserIsInvalid()

    def testMustContainAtSymbol(self):
        self.user.email = 'johndoe.example.org'
        self._assertUserIsInvalid()

    def testMustContainDomainName(self):
        self.user.email = 'johndoe@.org'
        self._assertUserIsInvalid()

    def testEmailMustContainDomain(self):
        self.user.email = 'johndoe@example'
        self._assertUserIsInvalid()

    def testEmailMustHaveOnlyOneAt(self):
        self.user.email = 'johndoe@@example.org'
        self._assertUserIsInvalid()


    def testCategoriesCannotStoreNonCategoryModels(self):
        with self.assertRaises(TypeError):
            self.user.categories.add(self.secondUser)

    def testCategoriesCanStoreOneCategoryModel(self):
        category = Category.objects.get(id=1)
        self.user.categories.add(category)
        self._assertUserIsValid()

    def testCategoriesCanStoreMoreThanOneCategoryModel(self):
        for i in range(15):
            spendingLimit = SpendingLimit.objects.create(amount=10+i, timePeriod='daily')
            category = Category.objects.create(name='testcategory'+str(i), spendingLimit=spendingLimit)
            self.user.categories.add(category)
            self._assertUserIsValid()
        
    
    def testFollowCounters(self):
        thirdUser = User.objects.create(
            username='lucywhite', 
            email='lucywhite@example.org', 
            firstName='Lucy',
            lastName='White',
            password='Password123',
        )
        self.user.followers.add(self.secondUser)
        self.secondUser.followers.add(thirdUser)
        self.secondUser.followers.add(self.user)
        self.assertEqual(thirdUser.followerCount(), 0)
        self.assertEqual(thirdUser.followeeCount(), 1)
        self.assertEqual(self.user.followerCount(), 1)
        self.assertEqual(self.user.followeeCount(), 1)
        self.assertEqual(self.secondUser.followerCount(), 2)
        self.assertEqual(self.secondUser.followeeCount(), 1)