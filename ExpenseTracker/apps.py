from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ExpensetrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ExpenseTracker'

    def ready(self):
        from ExpenseTracker.models import House
        from .defaultData import DEFAULT_HOUSES


        def createHouses(sender, **kwargs):
            # Create the default houses if they don't exist
            for house in DEFAULT_HOUSES:
                House.objects.get_or_create(**house)

         # Connect the create_default_houses function to the post_migrate signal
        post_migrate.connect(createHouses, sender=self)
