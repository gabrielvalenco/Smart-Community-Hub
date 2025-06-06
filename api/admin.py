from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ServiceProvider, CommunityEvent, Resource, Booking, Review

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('address', 'phone_number', 'bio', 'profile_image')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'service_type', 'user', 'is_available', 'created_at')
    list_filter = ('service_type', 'is_available')
    search_fields = ('business_name', 'service_type', 'description')
    raw_id_fields = ('user',)
    
    class Meta:
        verbose_name = 'Prestador de Serviço'
        verbose_name_plural = 'Prestadores de Serviços'

@admin.register(CommunityEvent)
class CommunityEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'location', 'start_date', 'end_date', 'is_free')
    list_filter = ('is_free', 'start_date')
    search_fields = ('title', 'description', 'location')
    raw_id_fields = ('organizer',)
    filter_horizontal = ('attendees',)
    
    class Meta:
        verbose_name = 'Evento Comunitário'
        verbose_name_plural = 'Eventos Comunitários'

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location', 'is_available', 'hourly_rate')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description', 'category', 'location')
    
    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'resource', 'start_time', 'end_time', 'status', 'total_cost')
    list_filter = ('status', 'start_time')
    search_fields = ('user__username', 'resource__name', 'notes')
    raw_id_fields = ('user', 'resource')
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_reviewed_item', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')
    raw_id_fields = ('user', 'service_provider', 'event')
    
    def get_reviewed_item(self, obj):
        if obj.service_provider:
            return f"Prestador: {obj.service_provider.business_name}"
        elif obj.event:
            return f"Evento: {obj.event.title}"
        return "Desconhecido"
    get_reviewed_item.short_description = "Item Avaliado"
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
