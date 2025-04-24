from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    UserViewSet, ServiceProviderViewSet, CommunityEventViewSet,
    ResourceViewSet, BookingViewSet, ReviewViewSet, index
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'providers', ServiceProviderViewSet)
router.register(r'events', CommunityEventViewSet)
router.register(r'resources', ResourceViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)

# Swagger schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Smart Community Hub API",
        default_version='v1',
        description="A RESTful API for managing shared resources and services within a small community",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', index, name='index'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    
    # Swagger documentation URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
