import re

from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.inspectors.field import SerializerInspector
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

from api.models import Item, Pet
from api.serializers import ItemSerializer, ItemQuerySerializer, PolymorphicSerializer, PolymorphicPetSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_id='items_list',
    query_serializer=ItemQuerySerializer()
))
class ItemListAPIView(ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        return Item.objects.all()


class PolymorphicSerializerInspector(SerializerInspector):
    def _get_definition_name(self, ref):
        m = re.search(r"#/definitions/(?P<definition_name>\w+)", ref)
        return m.group('definition_name')

    def _get_schema_ref(self, serializer):
        schema_ref = self.probe_inspectors(
            self.field_inspectors, 'get_schema', serializer, {
                'field_inspectors': self.field_inspectors
            }
        )
        return schema_ref

    def _get_schema(self, serializer, schema_ref=None):
        if schema_ref is None:
            schema_ref = self._get_schema_ref(serializer)
        schema = openapi.resolve_ref(schema_ref, self.components)
        return schema

    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(result, openapi.Schema.OR_REF) and issubclass(obj.__class__, PolymorphicSerializer):
            definitions = self.components._objects['definitions']
            definition_name = self._get_definition_name(result['$ref'])
            definitions.pop(definition_name, None)

            base_model_name = obj.to_discriminator(obj.base_serializer.Meta.model)
            base_ref = '#/definitions/{}'.format(base_model_name)
            if base_model_name not in definitions:
                schema = self._get_schema(obj.base_serializer)
                schema['discriminator'] = obj.discriminator_field
                schema['required'] = schema.setdefault('required', []) + [obj.discriminator_field]
                definitions[base_model_name] = schema

            for model, serializer in obj.derived_serializers_mapping.items():
                if serializer is None:
                    serializer = obj.base_serializer
                discriminator = obj.to_discriminator(model)
                if discriminator not in definitions:
                    schema_ref = self._get_schema_ref(serializer)
                    all_of = [
                        {'$ref': base_ref}
                    ]
                    if schema_ref['$ref'] != base_ref:
                        all_of.append(self._get_schema(serializer, schema_ref=schema_ref))
                    definitions[discriminator] = openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        allOf=all_of
                    )
            result['$ref'] = base_ref

        return result


class TestAutoSchema(SwaggerAutoSchema):
    field_inspectors = [PolymorphicSerializerInspector] + swagger_settings.DEFAULT_FIELD_INSPECTORS


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_id='pets_list',
    responses={200: PolymorphicPetSerializer}
))
class PetsListAPIView(ListAPIView):
    serializer_class = PolymorphicPetSerializer
    swagger_schema = TestAutoSchema

    def get_queryset(self):
        return Pet.objects.all()
