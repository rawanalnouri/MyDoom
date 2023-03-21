import decimal
import random
import datetime
from faker import Faker
from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta
from ExpenseTracker.models import *
from ExpenseTracker.helpers.seedingHelper import *

class Command(BaseCommand):
    PASSWORD = "Password123"
    SPENDING_LIMIT_COUNT = CATEGORY_COUNT = 50
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
        self.seedUserCategories()
        for followee in random.sample(list(User.objects.all()), random.randint(0, 10)):
            user.followers.add(followee)
        adminStuff = self.seedAdminUser()
        self.seedNotifications()
        # Create dummy share notifcation for base user
        ShareCategoryNotification.objects.create(
            toUser=user,
            fromUser = adminStuff[0],
            title="New Category Shared!",
            message = adminStuff[0].username + " wants to share a category '"+ adminStuff[1].name +"' with you",
            sharedCategory = adminStuff[1],
            type='category'
            )

    def seedAdminUser(self):
        firstName = 'admin'
        lastName = 'admin'
        email = self._email(firstName, lastName)
        username = 'admin'
        adminHouse=random.choice(list(House.objects.all()))
        admin = User.objects.create_superuser(
            username = username,
            firstName = firstName,
            lastName = lastName,
            email = email,
            password = Command.PASSWORD,
            house=adminHouse
        )
        category = Category.objects.create (
            name = "test",
            description = "test",
            spendingLimit = random.choice(list(SpendingLimit.objects.all())),
        )
        admin.categories.add(category)
        admin.save()
        category.users.add(admin)
        category.save()
        points=Points.objects.create(
            user = admin,
            count = random.randrange(1, 500),
        )
        adminHouse.points += points.count
        adminHouse.memberCount += 1
        adminHouse.save()
        self.stdout.write(self.style.SUCCESS(f"Created admin user: username {username}, password {Command.PASSWORD}"))
        return [admin, category]

    def seedBaseUser(self):
        firstName = 'John'
        lastName = 'Doe'
        email = self._email(firstName, lastName)
        username = 'johndoe'
        house = random.choice(list(House.objects.all()))
        user = User.objects.create_user(
            username = username,
            firstName = firstName,
            lastName = lastName,
            email = email,
            password = Command.PASSWORD,
            house = house,
        )
        points = Points.objects.create(
            user = user,
            count = random.randrange(1, 500),
        )
        house.points += points.count
        house.memberCount += 1
        house.save()
        self.stdout.write(self.style.SUCCESS(f"Created base user: username {username}, password {Command.PASSWORD}"))
        return user

    def seedUsers(self):
        userCount = 0
        while userCount < Command.USER_COUNT:
            firstName = self.faker.unique.first_name()
            lastName = self.faker.unique.last_name()
            email = self._email(firstName, lastName)
            username = self._username(firstName, lastName)
            house = random.choice(list(House.objects.all()))
            user = User.objects.create_user(
                username = username,
                firstName = firstName,
                lastName = lastName,
                email = email,
                password = Command.PASSWORD,
                house = house,
            )
            points = Points.objects.create(
                user = user,
                count = random.randrange(5, 500),
            )
            house.points += points.count
            house.memberCount += 1
            house.save()
            userCount += 1
            for followee in random.sample(list(User.objects.all()), User.objects.count()):
                user.followers.add(followee)
        self.stdout.write(self.style.SUCCESS(f"Number of created users: {userCount}"))

    def _email(self, firstName, lastName):
        email = f'{firstName}.{lastName}@example.org'
        return email

    def _username(self, firstName, lastName):
        username = f'{firstName.lower()}{lastName.lower()}'
        return username
    
    def seedUserCategories(self):
        for user in User.objects.all():
            _categories = Category.objects.filter(users__in=[user])
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
            categoryName = catergories[categoryCount] 
            self._createCategory(categoryName)
            categoryCount += 1
        self.stdout.write(self.style.SUCCESS(f"Number of created categories: {categoryCount}"))

    def _createCategory(self,name):
        name = name
        description = self.faker.sentence()
        spendingLimit = random.choice(list(SpendingLimit.objects.all()))
        user = random.choice(list(User.objects.all()))
        _expenditures = random.sample(list(Expenditure.objects.all()), random.randint(0, Expenditure.objects.count()))
        category = Category.objects.create (
            name = name,
            description = description,
            spendingLimit = spendingLimit,
        )
        category.users.add(user)
        for expenditure in _expenditures:
            category.expenditures.add(expenditure)

    def seedExpenditures(self, *args, **options):
        expenditureCount = 0
        dayDifference = 0
        while expenditureCount < Command.EXPENDITURE_COUNT:
            title = expenditures[expenditureCount]
            self._createExpenditure(dayDifference,title)
            expenditureCount += 1
            dayDifference -= 2
        self.stdout.write(self.style.SUCCESS(f"Number of created expenditures: {expenditureCount}"))

    def _createExpenditure(self, dayDifference, title):
        title = title
        description = self.faker.sentence()
        date = datetime.now() + relativedelta(days=dayDifference)
        amount = float(decimal.Decimal(random.randrange(1, 10000))/100)
        Expenditure.objects.create(
            title=title,
            description=description,
            date=date,
            amount=amount,
        )

    def seedNotifications(self):
        notificationsCreated = 0
        for user in User.objects.all():
            notificationCount = 0
            while notificationCount < Command.NOTIFICATION_COUNT:
                   self._createNotifcation(user, notificationCount)
                   notificationCount += 1
            notificationsCreated += Command.NOTIFICATION_COUNT
        self.stdout.write(self.style.SUCCESS(f"Number of created notifications: {notificationsCreated}"))
        
            
        
    def _createNotifcation(self, user, count):
        title = notificationTitles[count]
        message = notificationMessages[count]
        isSeen = random.choice([True, False])
        Notification.objects.create(
            toUser=user,
            title=title,
            message=message,
            isSeen = isSeen,
            type='basic'
        )
