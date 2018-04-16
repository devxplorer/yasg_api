from rest_framework.fields import Field


class PolymorphicField(Field):
    def __init__(self, discriminator, serializers_map, *args, **kwargs):
        self.discriminator = discriminator
        self.serializers_map = serializers_map
        super(PolymorphicField, self).__init__(*args, **kwargs)

    def get_attribute(self, instance):
        return instance.as_leaf_class()

    def to_representation(self, obj):
        key = self.discriminator(obj) if callable(self.discriminator) else getattr(obj, self.discriminator)
        serializer_class = self.serializers_map[key]
        serializer = serializer_class(instance=obj)
        return serializer.data
