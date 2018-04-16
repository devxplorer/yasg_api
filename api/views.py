from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from api.models import Item, Pet
from api.serializers import ItemSerializer, ItemQuerySerializer, PetSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_id='items_list',
    query_serializer=ItemQuerySerializer()
))
class ItemListAPIView(ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        return Item.objects.all()


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_id='pets_list',
))
class PetsListAPIView(ListAPIView):
    serializer_class = PetSerializer

    def get_queryset(self):
        return Pet.objects.all()
