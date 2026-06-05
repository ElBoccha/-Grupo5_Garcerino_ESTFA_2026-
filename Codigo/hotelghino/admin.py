from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Alojamiento, Habitacion, Promocion, SolicitudPropietario

class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('username', 'email', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información extra', {'fields': ('dni', 'telefono', 'rol')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información extra', {'fields': ('dni', 'telefono', 'rol')}),
    )

class SolicitudPropietarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'motivo', 'estado', 'fecha_solicitud')
    list_filter = ('estado', 'fecha_solicitud')
    search_fields = ('usuario__username', 'motivo')
    ordering = ('-fecha_solicitud',)

class AlojamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'estado', 'id_usuario', 'fecha_creacion')
    list_filter = ('estado', 'tipo')
    search_fields = ('nombre', 'descripcion', 'id_usuario__username')

class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero_habitacion', 'numero_piso', 'capacidad_maxima', 'tipo', 'precio_noche', 'id_alohamiento', 'id_usuario')
    list_filter = ('tipo',)
    search_fields = ('id_usuario__username',)

class PromocionAdmin(admin.ModelAdmin):
    list_display = ('descuento', 'fecha_inicio', 'fecha_finalizacion', 'id_alojamiento', 'id_usuario')
    list_filter = ('fecha_inicio', 'fecha_finalizacion')
    search_fields = ('id_usuario__username',)

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Alojamiento, AlojamientoAdmin)
admin.site.register(Habitacion, HabitacionAdmin)
admin.site.register(Promocion, PromocionAdmin)
admin.site.register(SolicitudPropietario, SolicitudPropietarioAdmin)