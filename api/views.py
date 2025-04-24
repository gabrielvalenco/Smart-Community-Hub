from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
# from django_filters.rest_framework import DjangoFilterBackend  # Comentado temporariamente

from .models import ServiceProvider, CommunityEvent, Resource, Booking, Review
from .serializers import (
    UserSerializer, ServiceProviderSerializer, CommunityEventSerializer,
    ResourceSerializer, BookingSerializer, ReviewSerializer
)

User = get_user_model()

# Frontend view
def index(request):
    return render(request, 'api/index.html')

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]  # Removido DjangoFilterBackend
    search_fields = ['username', 'email', 'first_name', 'last_name']
    # filterset_fields = ['username', 'email']  # Comentado temporariamente
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def attend_event(self, request, pk=None):
        user = self.get_object()
        try:
            event_id = request.data.get('event_id')
            event = CommunityEvent.objects.get(pk=event_id)
            
            if event.attendees.filter(pk=user.pk).exists():
                return Response({'message': 'User is already attending this event'}, status=status.HTTP_400_BAD_REQUEST)
            
            if event.max_attendees and event.attendees.count() >= event.max_attendees:
                return Response({'message': 'Event has reached maximum attendees'}, status=status.HTTP_400_BAD_REQUEST)
            
            event.attendees.add(user)
            return Response({'message': 'Successfully registered for event'}, status=status.HTTP_200_OK)
        except CommunityEvent.DoesNotExist:
            return Response({'message': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

class ServiceProviderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for service providers
    """
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    filter_backends = [filters.SearchFilter]  # Removido DjangoFilterBackend
    search_fields = ['business_name', 'service_type', 'description']
    # filterset_fields = ['service_type', 'is_available']  # Comentado temporariamente

class CommunityEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for community events
    """
    queryset = CommunityEvent.objects.all()
    serializer_class = CommunityEventSerializer
    filter_backends = [filters.SearchFilter]  # Removido DjangoFilterBackend
    search_fields = ['title', 'description', 'location']
    # filterset_fields = ['is_free', 'organizer']  # Comentado temporariamente
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()
        user = request.user
        
        if event.attendees.filter(pk=user.pk).exists():
            return Response({'message': 'User is already attending this event'}, status=status.HTTP_400_BAD_REQUEST)
        
        if event.max_attendees and event.attendees.count() >= event.max_attendees:
            return Response({'message': 'Event has reached maximum attendees'}, status=status.HTTP_400_BAD_REQUEST)
        
        event.attendees.add(user)
        return Response({'message': 'Successfully registered for event'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unregister(self, request, pk=None):
        event = self.get_object()
        user = request.user
        
        if not event.attendees.filter(pk=user.pk).exists():
            return Response({'message': 'User is not registered for this event'}, status=status.HTTP_400_BAD_REQUEST)
        
        event.attendees.remove(user)
        return Response({'message': 'Successfully unregistered from event'}, status=status.HTTP_200_OK)

class ResourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for resources
    """
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filter_backends = [filters.SearchFilter]  # Removido DjangoFilterBackend
    search_fields = ['name', 'description', 'category', 'location']
    # filterset_fields = ['category', 'is_available']  # Comentado temporariamente

class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for bookings
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [filters.SearchFilter]  # Removido DjangoFilterBackend
    # filterset_fields = ['user', 'resource', 'status']  # Comentado temporariamente
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        if booking.status == 'cancelled':
            return Response({'message': 'Booking is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        
        if booking.status == 'completed':
            return Response({'message': 'Cannot cancel a completed booking'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'cancelled'
        booking.save()
        return Response({'message': 'Booking cancelled successfully'}, status=status.HTTP_200_OK)

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reviews
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [filters.SearchFilter]  # Removido DjangoFilterBackend
    search_fields = ['comment']
    # filterset_fields = ['user', 'service_provider', 'event', 'rating']  # Comentado temporariamente
    
    def get_queryset(self):
        queryset = Review.objects.all()
        service_provider_id = self.request.query_params.get('service_provider_id')
        event_id = self.request.query_params.get('event_id')
        
        if service_provider_id:
            queryset = queryset.filter(service_provider_id=service_provider_id)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        return queryset
