from rest_framework import serializers

from api.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('name', 'status')


class ItemQuerySerializer(serializers.Serializer):
    status = serializers.ChoiceField(label='Status label', choices=Item.STATUSES, help_text='help text')
