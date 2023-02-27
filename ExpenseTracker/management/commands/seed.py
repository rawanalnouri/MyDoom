import decimal
import random
import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta
from ExpenseTracker.models import SpendingLimit, Expenditure, Category, User, Points

class Command(BaseCommand):
    PASSWORD = "Password123"
    SPENDING_LIMIT_COUNT = CATEGORY_COUNT = 50
    EXPENDITURE_COUNT = 50
    USER_COUNT = 10

    help = "Seeds the database for testing and development."

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.seedSpendingLimits()
        self.seedExpenditures()
        self.seedUsers()
        self.seedBaseUser()
        self.seedCategories()
        self.seedUserCategories()

    def seedBaseUser(self):
        firstName = 'John'
        lastName = 'Doe'
        email = self._email(firstName, lastName)
        username = 'johndoe'
        user = User.objects.create_user(
            username = username,
            firstName = firstName,
            lastName = lastName,
            email = email,
            password = Command.PASSWORD,
        )
        Points.objects.create(
            user = user,
            pointsNum = 50,
        )
        self.stdout.write(self.style.SUCCESS(f"Created base user: username {username}, password {Command.PASSWORD}"))

    def seedUsers(self):
        userCount = 0
        while userCount < Command.USER_COUNT:
            firstName = self.faker.unique.first_name()
            lastName = self.faker.unique.last_name()
            email = self._email(firstName, lastName)
            username = self._username(firstName, lastName)
            User.objects.create_user(
                username = username,
                firstName = firstName,
                lastName = lastName,
                email = email,
                password = Command.PASSWORD,
            )
            userCount += 1
        self.stdout.write(self.style.SUCCESS(f"Number of created users: {userCount}"))

    def _email(self, firstName, lastName):
        email = f'{firstName}.{lastName}@example.org'
        return email

    def _username(self, firstName, lastName):
        username = f'{firstName}_{lastName}'
        return username
    
    def seedUserCategories(self):
        for user in User.objects.all():
            _categories = Category.objects.filter(user=user)
            for category in _categories:
                user.categories.add(category)

    def seedSpendingLimits(self, *args, **options):
        spendingLimitCount = 0
        while spendingLimitCount < Command.SPENDING_LIMIT_COUNT:
            self._createSpendingLimit()
            spendingLimitCount += 1
        self.stdout.write(self.style.SUCCESS(f"Number of created spending limits: {spendingLimitCount}"))
    
    def _createSpendingLimit(self):
        timePeriod = random.choice(SpendingLimit.TIME_CHOICES)[0]
        amount = float(decimal.Decimal(random.randrange(1, 100000))/100)
        SpendingLimit.objects.create(timePeriod=timePeriod, amount=amount)

    def seedCategories(self, *args, **options):
        categoryCount = 0
        while categoryCount < Command.CATEGORY_COUNT:
            self._createCategory()
            categoryCount += 1
        self.stdout.write(self.style.SUCCESS(f"Number of created categories: {categoryCount}"))

    def _createCategory(self):
        name = self.faker.word()
        description = self.faker.sentence()
        spendingLimit = random.choice(list(SpendingLimit.objects.all()))
        user = random.choice(list(User.objects.all()))
        _expenditures = random.sample(list(Expenditure.objects.all()), random.randint(0, Expenditure.objects.count()))
        category = Category.objects.create (
            name = name,
            description = description,
            user = user,
            spendingLimit = spendingLimit,
        )
        for expenditure in _expenditures:
            category.expenditures.add(expenditure)

    def seedExpenditures(self, *args, **options):
        expenditureCount = 0
        dayDifference = 0
        while expenditureCount < Command.EXPENDITURE_COUNT:
            self._createExpenditure(dayDifference)
            expenditureCount += 1
            dayDifference += 2
        self.stdout.write(self.style.SUCCESS(f"Number of created expenditures: {expenditureCount}"))

    def _createExpenditure(self, dayDifference):
        title = self.faker.word()
        description = self.faker.sentence()
        date = datetime.date.today() + relativedelta(days=dayDifference)
        mood = random.choice(Expenditure.MOOD_CHOICES)[0]
        amount = float(decimal.Decimal(random.randrange(1, 10000))/100)
        Expenditure.objects.create(
            title=title,
            description=description,
            date=date,
            mood=mood,
            amount=amount,
        )
