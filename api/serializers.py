from rest_framework import serializers

from api.fields import PolymorphicField
from api.models import Item, Pet, Cat, Dog, Lizard


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('name', 'status')


class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = (
            'name',
        )


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = (
            'bark',
        )


class LizardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lizard
        fields = (
            'loves_rocks',
        )


class ItemQuerySerializer(serializers.Serializer):
    status = serializers.ChoiceField(label='Status label', choices=Item.STATUSES, help_text='help text')


class PetSerializer(serializers.ModelSerializer):
    pet_data = PolymorphicField(
        discriminator=lambda obj: obj.content_type.model,
        serializers_map={
            'cat': CatSerializer,
            'dog': DogSerializer,
            'lizard': LizardSerializer,
        }
    )

    class Meta:
        model = Pet
        fields = ('id', 'pet_data')
