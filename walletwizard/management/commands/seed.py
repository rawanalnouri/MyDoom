import decimal
import random
import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta
from walletwizard.models import *
from walletwizard.helpers.seedingHelper import *

class Command(BaseCommand):
    PASSWORD = "Password123"
    SPENDING_LIMIT_COUNT = CATEGORY_COUNT = 30
    EXPENDITURE_COUNT = 50
    USER_COUNT = 10
    NOTIFICATION_COUNT = 5

    help = "Seeds the database for testing and development."

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.seedSpendingLimits()
        self.seedExpenditures()
        user = self.seedBaseUser()
        self.seedUsers()
        self.seedCategories()
        admin = self.seedAdminSuperuser()
        self.seedNotifications()
        self._createDummyShareNotification(admin, user)

    '''Functions to seed groups of User model objects for seeder.'''

    def seedAdminSuperuser(self):
        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            firstName = 'Admin'
            lastName = 'Administrator'
            house = random.choice(list(House.objects.all()))
            admin = self._createUserAndRequiredObjects(firstName, lastName, house, 'admin')
            category = Category.objects.create (
                name = 'Test',
                description = 'This is a test category.',
                spendingLimit = random.choice(list(SpendingLimit.objects.all()))
            )
            admin.categories.add(category)
            category.users.add(admin)
            category.save()
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser: username {admin.username}, password {Command.PASSWORD}"))
            return admin

    def seedBaseUser(self):
        try:
            user = User.objects.get(username='johndoe')
        except User.DoesNotExist:
            firstName = 'John'
            lastName = 'Doe'
            house = random.choice(list(House.objects.all()))
            user = self._createUserAndRequiredObjects(firstName, lastName, house)
            self._updateFollowers(user)
            self.stdout.write(self.style.SUCCESS(f"Created base user: username {user.username}, password {Command.PASSWORD}"))
        return user

    def seedUsers(self):
        userCount = 0
        while userCount < Command.USER_COUNT:
            firstName = self.faker.unique.first_name()
            lastName = self.faker.unique.last_name()
            house = random.choice(list(House.objects.all()))
            user = self._createUserAndRequiredObjects(firstName, lastName, house)
            self._updateFollowers(user)
            userCount += 1
        self.stdout.write(self.style.SUCCESS(f"Number of created users: {userCount}"))

    '''Functions to seed groups of other model objects for seeder.'''

    def seedExpenditures(self):
        expenditureCount = 0
        dayDifference = 0
        while expenditureCount < Command.EXPENDITURE_COUNT:
            title = expenditures[expenditureCount]
            self._createExpenditure(dayDifference, title)
            expenditureCount += 1
            dayDifference -= 2
        self.stdout.write(self.style.SUCCESS(f"Number of created expenditures: {expenditureCount}"))

    def seedSpendingLimits(self):
        spendingLimitCount = 0
        while spendingLimitCount < Command.SPENDING_LIMIT_COUNT:
            self._createSpendingLimit()
            spendingLimitCount += 1
        self.stdout.write(self.style.SUCCESS(f"Number of created spending limits: {spendingLimitCount}"))

    def seedCategories(self):
        categoryCount = 0
        while categoryCount < Command.CATEGORY_COUNT:
            categoryName = catergories[categoryCount] 
            self._createCategory(categoryName)
            categoryCount += 1
        self.stdout.write(self.style.SUCCESS(f"Number of created categories: {categoryCount}"))

    def seedNotifications(self):
        notificationsCreated = 0
        for user in User.objects.all():
            notificationCount = 0
            while notificationCount < Command.NOTIFICATION_COUNT:
                   self._createNotification(user, notificationCount)
                   notificationCount += 1
            notificationsCreated += Command.NOTIFICATION_COUNT
        self.stdout.write(self.style.SUCCESS(f"Number of created notifications: {notificationsCreated}"))

    '''Functions to create individual objects for seeder.'''

    def _createUserAndRequiredObjects(self, firstName, lastName, house, username=''):
        email = self._email(firstName, lastName)
        if username == '':
            username = self._username(firstName, lastName)
        user = User.objects.create_user(
            username=username,
            firstName=firstName,
            lastName=lastName,
            email=email,
            password=Command.PASSWORD,
            house=house,
        )
        points = Points.objects.create(
            user=user,
            count=random.randrange(5, 500),
        )
        house.points += points.count
        house.memberCount += 1
        house.save()
        return user
    
    def _createSpendingLimit(self):
        timePeriod = random.choice(SpendingLimit.TIME_CHOICES)[0]
        amount = float(decimal.Decimal(random.randrange(1, 100000))/100)
        SpendingLimit.objects.create(timePeriod=timePeriod, amount=amount)

    def _createCategory(self, name):
        user = random.choice(list(User.objects.all()))
        category = Category.objects.create (
            name = name,
            description = self.faker.sentence(),
            spendingLimit = random.choice(list(SpendingLimit.objects.all())),
        )
        user.categories.add(category)
        category.users.add(user)
        user.save()
        sampleSize = random.randint(0, Expenditure.objects.count())
        expendituresToAdd = random.sample(list(Expenditure.objects.all()), sampleSize)
        for expenditure in expendituresToAdd:
            category.expenditures.add(expenditure)
        category.save()

    def _createExpenditure(self, dayDifference, title):
        Expenditure.objects.create(
            title=title,
            description=self.faker.sentence(),
            date=datetime.now() + relativedelta(days=dayDifference),
            amount=float(decimal.Decimal(random.randrange(1, 10000))/100),
        )
        
    def _createNotification(self, user, count):
        Notification.objects.create(
            toUser = user,
            title = notificationTitles[count],
            message = notificationMessages[count],
            isSeen = random.choice([True, False]),
            type = 'basic'
        )
    
    def _createDummyShareNotification(self, fromUser, toUser):
        ShareCategoryNotification.objects.create(
            toUser=toUser,
            fromUser=fromUser,
            title="New Category Shared!",
            message=f"{fromUser.username} wants to share a category '{fromUser.categories.first().name}' with you",
            sharedCategory=fromUser.categories.first(),
            type='category'
        )
    
    '''Helper functions to create user for seeder.'''

    def _updateFollowers(self, user):
        for followee in random.sample(list(User.objects.all()), User.objects.count()):
            if user != followee:
                user.followers.add(followee)
        user.save()

    def _email(self, firstName, lastName):
        email = f'{firstName}.{lastName}@example.org'
        return email

    def _username(self, firstName, lastName):
        username = f'{firstName.lower()}{lastName.lower()}'
        return username