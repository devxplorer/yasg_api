from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api.views import ItemListAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="Items API",
        default_version='v1',
        description="Test description",
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^items/', ItemListAPIView.as_view(), name='items'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc'), name='schema-redoc'),
]
