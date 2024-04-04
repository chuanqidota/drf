from django.apps import AppConfig


class ConsumerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.consumer'

    def ready(self):
        super(ConsumerConfig, self).ready()


