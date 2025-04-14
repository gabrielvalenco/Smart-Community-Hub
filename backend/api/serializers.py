from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ServiceProvider, Resource, CommunityEvent, Booking, Review, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the UserProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'address', 'phone_number', 'profile_picture', 'interests', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class ServiceProviderSerializer(serializers.ModelSerializer):
    """Serializer for the ServiceProvider model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceProvider
        fields = ['id', 'user', 'user_id', 'business_name', 'description', 'service_type', 
                  'hourly_rate', 'phone_number', 'website', 'is_available', 
                  'created_at', 'updated_at', 'average_rating']
        read_only_fields = ['created_at', 'updated_at', 'average_rating']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / len(reviews)


class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for the Resource model"""
    
    class Meta:
        model = Resource
        fields = ['id', 'name', 'slug', 'description', 'resource_type', 'location', 
                  'capacity', 'hourly_rate', 'daily_rate', 'is_available', 
                  'image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'slug']


class CommunityEventSerializer(serializers.ModelSerializer):
    """Serializer for the CommunityEvent model"""
    organizer = UserSerializer(read_only=True)
    organizer_id = serializers.IntegerField(write_only=True)
    attendee_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CommunityEvent
        fields = ['id', 'title', 'slug', 'description', 'organizer', 'organizer_id',
                  'location', 'start_time', 'end_time', 'max_attendees', 
                  'is_free', 'fee', 'image', 'created_at', 'updated_at',
                  'attendee_count', 'is_full']
        read_only_fields = ['created_at', 'updated_at', 'slug', 'attendee_count', 'is_full']
    
    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time.")
        if not data['is_free'] and (data.get('fee') is None or data.get('fee') <= 0):
            raise serializers.ValidationError("Fee must be provided and greater than 0 for non-free events.")
        return data


class EventAttendeeSerializer(serializers.Serializer):
    """Serializer for adding/removing attendees from events"""
    user_id = serializers.IntegerField()


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for the Booking model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    resource = ResourceSerializer(read_only=True)
    resource_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'user_id', 'resource', 'resource_id', 'start_time', 
                  'end_time', 'status', 'total_cost', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'total_cost']
    
    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time.")
        
        # Check for overlapping bookings
        resource_id = data['resource_id']
        start_time = data['start_time']
        end_time = data['end_time']
        
        overlapping_bookings = Booking.objects.filter(
            resource_id=resource_id,
            status__in=['PENDING', 'CONFIRMED'],
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        # Exclude current booking in case of update
        if self.instance:
            overlapping_bookings = overlapping_bookings.exclude(id=self.instance.id)
        
        if overlapping_bookings.exists():
            raise serializers.ValidationError("This resource is already booked for the selected time period.")
        
        return data
    
    def create(self, validated_data):
        # Calculate total cost based on booking duration
        resource = Resource.objects.get(id=validated_data['resource_id'])
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']
        
        # Calculate duration in hours
        duration_hours = (end_time - start_time).total_seconds() / 3600
        
        # Calculate total cost based on hourly rate
        if resource.hourly_rate:
            validated_data['total_cost'] = resource.hourly_rate * duration_hours
        
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    service_provider_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    event_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_id', 'service_provider_id', 'event_id', 
                  'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        # Ensure at least one of service_provider_id or event_id is provided
        if not data.get('service_provider_id') and not data.get('event_id'):
            raise serializers.ValidationError("Either service_provider_id or event_id must be provided.")
        
        # Ensure not both are provided
        if data.get('service_provider_id') and data.get('event_id'):
            raise serializers.ValidationError("Only one of service_provider_id or event_id should be provided.")
        
        # Check for duplicate reviews
        user_id = data['user_id']
        
        if data.get('service_provider_id'):
            existing_review = Review.objects.filter(
                user_id=user_id,
                service_provider_id=data['service_provider_id']
            ).exists()
            if existing_review:
                raise serializers.ValidationError("You have already reviewed this service provider.")
        
        if data.get('event_id'):
            existing_review = Review.objects.filter(
                user_id=user_id,
                event_id=data['event_id']
            ).exists()
            if existing_review:
                raise serializers.ValidationError("You have already reviewed this event.")
        
        return data
