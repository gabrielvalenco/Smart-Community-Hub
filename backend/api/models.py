from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class ServiceProvider(models.Model):
    """
    Model representing local professionals offering services
    One-to-One relationship with User
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider')
    business_name = models.CharField(max_length=100)
    description = models.TextField()
    service_type = models.CharField(max_length=50)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name


class Resource(models.Model):
    """
    Model representing shared resources that can be booked
    """
    RESOURCE_TYPES = [
        ('SPACE', 'Coworking Space'),
        ('EQUIPMENT', 'Equipment'),
        ('VEHICLE', 'Vehicle'),
        ('TOOL', 'Tool'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    location = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='resources/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CommunityEvent(models.Model):
    """
    Model representing events organized by or for residents
    Many-to-Many relationship with User (attendees)
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    location = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_attendees = models.PositiveIntegerField(blank=True, null=True)
    attendees = models.ManyToManyField(User, related_name='events_attending', blank=True)
    is_free = models.BooleanField(default=True)
    fee = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    @property
    def attendee_count(self):
        return self.attendees.count()
    
    @property
    def is_full(self):
        if self.max_attendees:
            return self.attendee_count >= self.max_attendees
        return False


class Booking(models.Model):
    """
    Model representing reservations for shared resources
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.resource.name} ({self.start_time.strftime('%Y-%m-%d')})"
    
    class Meta:
        ordering = ['-start_time']
        # Ensure no overlapping bookings for the same resource
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='check_end_time_after_start_time'
            )
        ]


class Review(models.Model):
    """
    Model representing feedback on services or events
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.service_provider:
            return f"Review for {self.service_provider.business_name} by {self.user.username}"
        elif self.event:
            return f"Review for {self.event.title} by {self.user.username}"
        return f"Review by {self.user.username}"
    
    class Meta:
        # Ensure a user can only review a service provider once
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'service_provider'],
                condition=models.Q(service_provider__isnull=False),
                name='unique_user_service_provider_review'
            ),
            models.UniqueConstraint(
                fields=['user', 'event'],
                condition=models.Q(event__isnull=False),
                name='unique_user_event_review'
            ),
            models.CheckConstraint(
                check=models.Q(service_provider__isnull=False) | models.Q(event__isnull=False),
                name='check_review_has_target'
            )
        ]


class UserProfile(models.Model):
    """
    Extended profile for User model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    interests = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
