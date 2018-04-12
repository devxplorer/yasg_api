from django.db import models


class Item(models.Model):
    STATUSES = (
        (1, 'First'),
        (2, 'Second'),
        (3, 'Third'),
    )

    name = models.CharField(max_length=128)
    status = models.IntegerField(choices=STATUSES)
