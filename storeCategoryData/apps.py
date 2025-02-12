from django.apps import AppConfig


class StorecategorydataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "storeCategoryData"

    def ready(self):
        import storeCategoryData.signals

