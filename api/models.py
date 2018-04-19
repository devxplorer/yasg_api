from django.db import models
from django.contrib.contenttypes.models import ContentType

class Item(models.Model):
    STATUSES = (
        (1, 'First'),
        (2, 'Second'),
        (3, 'Third'),
    )

    name = models.CharField(max_length=128)
    status = models.IntegerField(choices=STATUSES)
    pet = models.ForeignKey('api.Pet', related_name='items', null=True, blank=True)


class PolymorphicModel(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, editable=False)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if (not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        self.save_base(force_insert=force_insert, force_update=force_update, using=using)

    def as_leaf_class(self):
        model = self.content_type.model_class()
        return model.objects.get(id=self.id)


class Pet(PolymorphicModel):
    @property
    def pet_type(self):
        return self.content_type.model.capitalize()


class Ordinary(Pet):
    pass


class Cat(Pet):
    name = models.CharField(max_length=128)


class Dog(Pet):
    bark = models.CharField(max_length=128)


class Lizard(Pet):
    loves_rocks = models.BooleanField(default=True)
