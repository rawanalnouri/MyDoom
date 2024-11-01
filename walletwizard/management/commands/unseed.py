from django.core.management.base import BaseCommand
from walletwizard.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        self._deleteExpenditures()
        self._deleteCategories()
        self._deleteUsers()
        self._deleteNotifications()
        self._resetHouse()
    
    def _deleteExpenditures(self, *args, **options):
        deletedExpenditures = 0
        for expenditure in Expenditure.objects.all():
                expenditure.delete()
                deletedExpenditures += 1
        self.stdout.write(self.style.SUCCESS(f"Number of deleted expenditures: {deletedExpenditures}"))
    
    def _deleteCategories(self, *args, **options):
        deletedCategories = 0
        for category in Category.objects.all():
                category.delete()
                deletedCategories += 1
        self.stdout.write(self.style.SUCCESS(f"Number of deleted categories: {deletedCategories}"))
    
    def _deleteUsers(self, *args, **options):
        deletedUsers = 0
        for user in User.objects.all():
                user.delete()
                deletedUsers += 1
        self.stdout.write(self.style.SUCCESS(f"Number of deleted users: {deletedUsers}"))

    def _deleteNotifications(self, *args, **options):
        deletedNotifications = 0
        for notification in Notification.objects.all():
                notification.delete()
                deletedNotifications += 1
        self.stdout.write(self.style.SUCCESS(f"Number of deleted notifications: {deletedNotifications}"))

    def _resetHouse(self, *args, **options):
        resetHouses = 0
        for house in House.objects.all():
                house.points=0
                house.memberCount=0
                house.save()
                resetHouses += 1
        self.stdout.write(self.style.SUCCESS(f"Number of reset houses: {resetHouses}"))