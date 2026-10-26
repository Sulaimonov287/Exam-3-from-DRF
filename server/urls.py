from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Nastroika JWT-avtorizacii dlya Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="E-commerce API",
        default_version='v1',
        description="Dokumentaciya API dlya internet-magazina",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],  # Ubiraet standartnuyu Basic auth iz Swagger UI
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]