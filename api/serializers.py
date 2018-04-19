from collections import Mapping

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from rest_framework import serializers
from six import string_types

from api.helpers import merge_dicts
from api.models import Item, Pet, Cat, Dog, Lizard, Ordinary


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('name', 'status')


class ItemQuerySerializer(serializers.Serializer):
    status = serializers.ChoiceField(label='Status label', choices=Item.STATUSES, help_text='help text')


class PolymorphicSerializer(serializers.Serializer):
    discriminator_field = None
    base_serializer_class = None
    derived_serializers_mapping = None

    def __new__(cls, *args, **kwargs):
        if cls.base_serializer_class is None:
            raise ImproperlyConfigured(
                '`{cls}` is missing a '
                '`{cls}.base_serializer_class` attribute'.format(
                    cls=cls.__name__
                )
            )
        if cls.derived_serializers_mapping is None:
            raise ImproperlyConfigured(
                '`{cls}` is missing a '
                '`{cls}.derived_serializers_mapping` attribute'.format(
                    cls=cls.__name__
                )
            )
        if not isinstance(cls.discriminator_field, string_types):
            raise ImproperlyConfigured(
                '`{cls}.discriminator_field` must be a string'.format(
                    cls=cls.__name__
                )
            )
        return super(PolymorphicSerializer, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(PolymorphicSerializer, self).__init__(*args, **kwargs)

        derived_serializers_mapping = self.derived_serializers_mapping
        self.derived_serializers_mapping = {}
        self.discriminator_model_mapping = {}
        self.base_serializer = self.base_serializer_class(*args, **kwargs)

        for model, serializer in derived_serializers_mapping.items():
            discriminator = self.to_discriminator(model)
            if callable(serializer):
                serializer = serializer(*args, **kwargs)

            self.discriminator_model_mapping[discriminator] = model
            self.derived_serializers_mapping[model] = serializer

    def to_discriminator(self, model_or_instance):
        return model_or_instance._meta.object_name

    def to_representation(self, instance):
        instance = instance.as_leaf_class()

        if isinstance(instance, Mapping):
            discriminator = self._get_discriminator_from_mapping(instance)
            serializer = self._get_serializer_from_discriminator(discriminator)
        else:
            serializer = self._get_serializer_from_model_or_instance(instance)

        ret1 = self.base_serializer.to_representation(instance)
        ret2 = serializer.to_representation(instance)
        ret = merge_dicts(ret2, ret1)
        return ret

    def to_internal_value(self, data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError

    def is_valid(self, *args, **kwargs):
        valid = super(PolymorphicSerializer, self).is_valid(*args, **kwargs)
        try:
            discriminator = self._get_discriminator_from_mapping(self.validated_data)
            serializer = self._get_serializer_from_discriminator(discriminator)
        except serializers.ValidationError:
            child_valid = False
        else:
            child_valid = serializer.is_valid(*args, **kwargs)
            self._errors.update(serializer.errors)
        return valid and child_valid

    def _to_model(self, model_or_instance):
        return (model_or_instance.__class__
                if isinstance(model_or_instance, models.Model)
                else model_or_instance)

    def _get_discriminator_from_mapping(self, mapping):
        try:
            return mapping[self.discriminator_field]
        except KeyError:
            raise serializers.ValidationError({
                self.discriminator_field: 'This field is required',
            })

    def _get_serializer_from_model_or_instance(self, model_or_instance):
        model = self._to_model(model_or_instance)

        for klass in model.mro():
            if klass in self.derived_serializers_mapping:
                return self.derived_serializers_mapping[klass]

        raise KeyError(
            '`{cls}.derived_serializers_mapping` is missing '
            'a corresponding serializer for `{model}` model'.format(
                cls=self.__class__.__name__,
                model=model.__name__
            )
        )

    def _get_serializer_from_discriminator(self, discriminator):
        try:
            model = self.discriminator_model_mapping[discriminator]
        except KeyError:
            raise serializers.ValidationError({
                self.discriminator_field: 'Invalid {0}'.format(
                    self.discriminator_field
                )
            })

        return self._get_serializer_from_model_or_instance(model)


class PetSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Pet
        fields = (
            'id',
            'pet_type',
            'items',
        )


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


class PolymorphicPetSerializer(PolymorphicSerializer):
    discriminator_field = 'pet_type'
    base_serializer_class = PetSerializer
    derived_serializers_mapping = {
        Ordinary: None,
        Cat: CatSerializer,
        Dog: DogSerializer,
        Lizard: LizardSerializer,
    }
