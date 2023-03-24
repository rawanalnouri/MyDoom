'''Unit tests of the Category model'''
from walletwizard.models import Category, SpendingLimit, Expenditure, User
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime
from walletwizard.tests.testHelpers import createUsers

class CategoryModelTestCase(TestCase):
    '''Unit tests of the Category model'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)

    def testNameCannotBeBlank(self):
        self.category.name = ''
        self._assertCategoryIsInvalid()
    
    def testNameCannotBeNone(self):
        self.category.name = None
        self._assertCategoryIsInvalid()
    
    def testNameNeedNotBeUnique(self):
        secondSpendingLimit = SpendingLimit.objects.create(amount=100, timePeriod='weekly')
        secondCategory = Category.objects.create(name='secondCategory', spendingLimit=secondSpendingLimit)
        self.category.name = secondCategory.name
        self._assertCategoryIsValid()
    
    def testNameMustBeAtMostFiftyCharactersLong(self):
        self.category.name = 'x' * 51
        self._assertCategoryIsInvalid()
    
    def testNameCanBeLessThanFiftyCharactersLong(self):
        self.category.name = 'x' * 25
        self._assertCategoryIsValid()
    
    def testNameCanBeFiftyCharactersLong(self):
        self.category.name = 'x' * 50
        self._assertCategoryIsValid()

    def testSpendingLimitCannotNone(self):
        self.category.spendingLimit = None
        self._assertCategoryIsInvalid()

    def testExpendituresCannotStoreNonExpenditureModels(self):
        with self.assertRaises(TypeError):
            self.category.expenditures.add(self.user)

    def testExpendituresCanStoreOneExpenditureModel(self):
        self.category.expenditures.add(self.expenditure)
        self._assertCategoryIsValid()

    def testExpendituresCanStoreMoreThanOneExpenditureModel(self):
        for i in range(15):
            expenditure = Expenditure.objects.create(title='testexpenditure' + str(i), date=datetime.today(), amount=10)
            self.category.expenditures.add(expenditure)
            self._assertCategoryIsValid()

    def testUsersCannotStoreNonUserModels(self):
        with self.assertRaises(TypeError):
            self.category.users.add(self.expenditure)

    def testUsersCanStoreOneUserModel(self):
        self.category.users.add(self.user)
        self._assertCategoryIsValid()

    def testUsersCanStoreMoreThanOneUserModel(self):
        users = createUsers(15)
        self.category.users.add(*users)
        self._assertCategoryIsValid()

    def testDescriptionCanBeBlank(self):
        self.category.description = ''
        self._assertCategoryIsValid()

    def testDescriptionMustBeAtMost250CharactersLong(self):
        self.category.description = 'x' * 251
        self._assertCategoryIsInvalid()

    def testDescriptionCanBeLessThan250CharactersLong(self):
        self.category.description = 'x' * 200
        self._assertCategoryIsValid()

    def testDescriptionCanBe250CharactersLong(self):
        self.category.description = 'x' * 250
        self._assertCategoryIsValid()
    
    def testDescriptionNeedNotBeUnique(self):
        secondSpendingLimit = SpendingLimit.objects.create(
            amount=100, 
            timePeriod='weekly'
        )
        secondCategory = Category.objects.create(
            name='secondCategory', 
            description='This is the second category\'s description.',
            spendingLimit=secondSpendingLimit,
        )
        self.category.description = secondCategory.description
        self._assertCategoryIsValid()
    
    def testSpendingLimitCannotBeNone(self):
        self.category.spendingLimit = None
        self._assertCategoryIsInvalid()

    def _assertCategoryIsValid(self):
        self.category.full_clean()

    
    def _assertCategoryIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.category.full_clean() 
