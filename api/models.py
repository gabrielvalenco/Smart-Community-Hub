from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class User(AbstractUser):
    """
    Extended User model for community residents.
    """
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    def __str__(self):
        return self.username

class ServiceProvider(models.Model):
    """
    Model for local professionals offering services (e.g., tutors, electricians).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider')
    business_name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=100)
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.business_name

class CommunityEvent(models.Model):
    """
    Model for events organized by or for residents.
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    is_free = models.BooleanField(default=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    attendees = models.ManyToManyField(User, related_name='attending_events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Resource(models.Model):
    """
    Model for shared resources that can be booked (e.g., coworking spaces, bikes, tools).
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='resource_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Booking(models.Model):
    """
    Model for reservations of shared resources.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
            ('completed', 'Completed'),
        ],
        default='pending'
    )
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.resource.name} ({self.start_time})"
    
    class Meta:
        ordering = ['-start_time']

class Review(models.Model):
    """
    Model for feedback on services or events.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        reviewed_item = self.service_provider if self.service_provider else self.event
        return f"{self.user.username}'s review of {reviewed_item}"
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(service_provider__isnull=False, event__isnull=True) | 
                    models.Q(service_provider__isnull=True, event__isnull=False)
                ),
                name='review_either_provider_or_event'
            ),
            models.UniqueConstraint(
                fields=['user', 'service_provider'],
                name='unique_user_provider_review',
                condition=models.Q(service_provider__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_user_event_review',
                condition=models.Q(event__isnull=False)
            ),
        ]
