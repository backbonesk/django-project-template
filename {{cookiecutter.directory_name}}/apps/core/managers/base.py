import random
from django.db import models


class BaseManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self._alive_only = kwargs.pop('alive_only', True)
        super(BaseManager, self).__init__(*args, **kwargs)

    def random(self):
        return random.choice(self.all())
