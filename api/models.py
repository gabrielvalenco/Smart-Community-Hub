from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class User(AbstractUser):
    """
    Extended User model for community residents.
    """
    address = models.CharField(max_length=255, blank=True, verbose_name='Endereço')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    bio = models.TextField(blank=True, verbose_name='Biografia')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name='Imagem de Perfil')
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class ServiceProvider(models.Model):
    """
    Model for local professionals offering services (e.g., tutors, electricians).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider', verbose_name='Usuário')
    business_name = models.CharField(max_length=100, verbose_name='Nome do Negócio')
    service_type = models.CharField(max_length=100, verbose_name='Tipo de Serviço')
    description = models.TextField(verbose_name='Descrição')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Taxa Horária')
    is_available = models.BooleanField(default=True, verbose_name='Disponível')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    def __str__(self):
        return self.business_name
    
    class Meta:
        verbose_name = 'Prestador de Serviço'
        verbose_name_plural = 'Prestadores de Serviços'

class CommunityEvent(models.Model):
    """
    Model for events organized by or for residents.
    """
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(verbose_name='Descrição')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events', verbose_name='Organizador')
    location = models.CharField(max_length=255, verbose_name='Local')
    start_date = models.DateTimeField(verbose_name='Data de Início')
    end_date = models.DateTimeField(verbose_name='Data de Término')
    max_attendees = models.PositiveIntegerField(null=True, blank=True, verbose_name='Máximo de Participantes')
    is_free = models.BooleanField(default=True, verbose_name='Gratuito')
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Taxa')
    attendees = models.ManyToManyField(User, related_name='attending_events', blank=True, verbose_name='Participantes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Evento Comunitário'
        verbose_name_plural = 'Eventos Comunitários'

class Resource(models.Model):
    """
    Model for shared resources that can be booked (e.g., coworking spaces, bikes, tools).
    """
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(verbose_name='Descrição')
    category = models.CharField(max_length=100, verbose_name='Categoria')
    location = models.CharField(max_length=255, verbose_name='Local')
    is_available = models.BooleanField(default=True, verbose_name='Disponível')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Taxa Horária')
    image = models.ImageField(upload_to='resource_images/', blank=True, null=True, verbose_name='Imagem')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'

class Booking(models.Model):
    """
    Model for reservations of shared resources.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name='Usuário')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings', verbose_name='Recurso')
    start_time = models.DateTimeField(verbose_name='Hora de Início')
    end_time = models.DateTimeField(verbose_name='Hora de Término')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendente'),
            ('confirmed', 'Confirmado'),
            ('cancelled', 'Cancelado'),
            ('completed', 'Concluído'),
        ],
        default='pending',
        verbose_name='Status'
    )
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Custo Total')
    notes = models.TextField(blank=True, verbose_name='Observações')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    def __str__(self):
        return f"{self.user.username} - {self.resource.name} ({self.start_time})"
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

class Review(models.Model):
    """
    Model for feedback on services or events.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given', verbose_name='Usuário')
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True, verbose_name='Prestador de Serviço')
    event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True, verbose_name='Evento')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Avaliação')
    comment = models.TextField(verbose_name='Comentário')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
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
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
