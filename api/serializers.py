from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ServiceProvider, CommunityEvent, Resource, Booking, Review

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'address', 'phone_number', 'bio', 'profile_image']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class ServiceProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user',
        write_only=True
    )
    
    class Meta:
        model = ServiceProvider
        fields = ['id', 'user', 'user_id', 'business_name', 'service_type', 'description', 
                  'hourly_rate', 'is_available', 'created_at', 'updated_at']

class CommunityEventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    organizer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='organizer',
        write_only=True
    )
    attendees = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = CommunityEvent
        fields = ['id', 'title', 'description', 'organizer', 'organizer_id', 'location', 
                  'start_date', 'end_date', 'max_attendees', 'is_free', 'fee', 
                  'attendees', 'created_at', 'updated_at']
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'description', 'category', 'location', 
                  'is_available', 'hourly_rate', 'image', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    resource = ResourceSerializer(read_only=True)
    resource_id = serializers.PrimaryKeyRelatedField(
        queryset=Resource.objects.all(),
        source='resource',
        write_only=True
    )
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'user_id', 'resource', 'resource_id', 'start_time', 
                  'end_time', 'status', 'total_cost', 'notes', 'created_at', 'updated_at']
    
    def validate(self, data):
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("End time must be after start time")
                
            # Check for overlapping bookings
            resource = data.get('resource')
            if resource:
                overlapping_bookings = Booking.objects.filter(
                    resource=resource,
                    status__in=['pending', 'confirmed'],
                    start_time__lt=data['end_time'],
                    end_time__gt=data['start_time']
                )
                
                # Exclude current booking if updating
                if self.instance:
                    overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
                
                if overlapping_bookings.exists():
                    raise serializers.ValidationError("This resource is already booked for this time period")
        
        return data

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    service_provider = ServiceProviderSerializer(read_only=True)
    service_provider_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceProvider.objects.all(),
        source='service_provider',
        write_only=True,
        required=False
    )
    event = CommunityEventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=CommunityEvent.objects.all(),
        source='event',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_id', 'service_provider', 'service_provider_id', 
                  'event', 'event_id', 'rating', 'comment', 'created_at', 'updated_at']
    
    def validate(self, data):
        service_provider = data.get('service_provider')
        event = data.get('event')
        
        if not service_provider and not event:
            raise serializers.ValidationError("Either service provider or event must be provided")
        
        if service_provider and event:
            raise serializers.ValidationError("Review can only be for either a service provider or an event, not both")
        
        # Check for duplicate reviews
        user = data.get('user')
        if user:
            if service_provider:
                if Review.objects.filter(user=user, service_provider=service_provider).exists():
                    if not self.instance or self.instance.service_provider != service_provider or self.instance.user != user:
                        raise serializers.ValidationError("You have already reviewed this service provider")
            
            if event:
                if Review.objects.filter(user=user, event=event).exists():
                    if not self.instance or self.instance.event != event or self.instance.user != user:
                        raise serializers.ValidationError("You have already reviewed this event")
        
        return data
