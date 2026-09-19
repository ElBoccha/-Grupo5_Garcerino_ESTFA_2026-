from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.html import format_html
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
    list_display = ('usuario', 'motivo', 'estado', 'fecha_solicitud', 'acciones')
    list_filter = ('estado', 'fecha_solicitud')
    search_fields = ('usuario__username', 'motivo')
    ordering = ('-fecha_solicitud',)
    readonly_fields = ('usuario', 'motivo', 'estado', 'fecha_solicitud')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:solicitud_id>/aprobar/',
                self.admin_site.admin_view(self.aprobar_solicitud),
                name='hotelghino_solicitudpropietario_aprobar',
            ),
            path(
                '<int:solicitud_id>/rechazar/',
                self.admin_site.admin_view(self.rechazar_solicitud),
                name='hotelghino_solicitudpropietario_rechazar',
            ),
        ]
        return custom_urls + urls

    def acciones(self, obj):
        if obj.estado != 'P':
            return obj.get_estado_display()

        aprobar_url = reverse('admin:hotelghino_solicitudpropietario_aprobar', args=[obj.pk])
        rechazar_url = reverse('admin:hotelghino_solicitudpropietario_rechazar', args=[obj.pk])

        return format_html(
            '<a class="button" href="{}">Aceptar</a>&nbsp;'
            '<a class="button" href="{}">Rechazar</a>',
            aprobar_url,
            rechazar_url,
        )

    acciones.short_description = 'Acciones'

    def aprobar_solicitud(self, request, solicitud_id):
        solicitud = get_object_or_404(SolicitudPropietario, pk=solicitud_id)
        if solicitud.estado != 'P':
            messages.warning(request, 'La solicitud ya fue revisada.')
            return redirect('admin:hotelghino_solicitudpropietario_changelist')

        solicitud.estado = 'A'
        solicitud.save(update_fields=['estado'])

        usuario = solicitud.usuario
        usuario.rol = 'P'
        usuario.save(update_fields=['rol'])

        messages.success(request, f'Solicitud de {usuario.username} aprobada. Ahora es propietario.')
        return redirect('admin:hotelghino_solicitudpropietario_changelist')

    def rechazar_solicitud(self, request, solicitud_id):
        solicitud = get_object_or_404(SolicitudPropietario, pk=solicitud_id)
        if solicitud.estado != 'P':
            messages.warning(request, 'La solicitud ya fue revisada.')
            return redirect('admin:hotelghino_solicitudpropietario_changelist')

        solicitud.estado = 'R'
        solicitud.save(update_fields=['estado'])

        messages.success(request, f'Solicitud de {solicitud.usuario.username} rechazada.')
        return redirect('admin:hotelghino_solicitudpropietario_changelist')

class AlojamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'estado', 'id_usuario', 'fecha_creacion', 'acciones')
    list_filter = ('estado', 'tipo')
    search_fields = ('nombre', 'descripcion', 'id_usuario__username')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:alojamiento_id>/aprobar/',
                self.admin_site.admin_view(self.aprobar_alojamiento),
                name='hotelghino_alojamiento_aprobar',
            ),
            path(
                '<int:alojamiento_id>/rechazar/',
                self.admin_site.admin_view(self.rechazar_alojamiento),
                name='hotelghino_alojamiento_rechazar',
            ),
        ]
        return custom_urls + urls

    def acciones(self, obj):
        if obj.estado != 'P':
            return obj.get_estado_display()

        aprobar_url = reverse('admin:hotelghino_alojamiento_aprobar', args=[obj.pk])
        rechazar_url = reverse('admin:hotelghino_alojamiento_rechazar', args=[obj.pk])

        return format_html(
            '<a class="button" href="{}">Aprobar</a>&nbsp;'
            '<a class="button" href="{}">Rechazar</a>',
            aprobar_url,
            rechazar_url,
        )

    acciones.short_description = 'Acciones'

    def aprobar_alojamiento(self, request, alojamiento_id):
        alojamiento = get_object_or_404(Alojamiento, pk=alojamiento_id)
        alojamiento.estado = 'A'
        alojamiento.fecha_aprobacion = timezone.now()
        alojamiento.save(update_fields=['estado', 'fecha_aprobacion'])
        messages.success(request, f'Hotel "{alojamiento.nombre}" aprobado.')
        return redirect('admin:hotelghino_alojamiento_changelist')

    def rechazar_alojamiento(self, request, alojamiento_id):
        alojamiento = get_object_or_404(Alojamiento, pk=alojamiento_id)
        alojamiento.estado = 'R'
        alojamiento.save(update_fields=['estado'])
        messages.success(request, f'Hotel "{alojamiento.nombre}" rechazado.')
        return redirect('admin:hotelghino_alojamiento_changelist')

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
