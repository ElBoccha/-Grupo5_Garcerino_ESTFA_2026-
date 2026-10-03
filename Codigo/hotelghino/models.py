from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Usuario(AbstractUser):
    """
    Modelo personalizado de usuario para el sistema Hotelghino.
    Extiende AbstractUser de Django agregando DNI, teléfono y rol en la plataforma.
    """
    dni = models.IntegerField()
    telefono = models.CharField(max_length=15)
    
    ROLES = (
        ('H', 'Huesped'),
        ('P', 'Propietario'),
        ('A', 'Administrador'),
    )
    rol = models.CharField(
        max_length=1,
        choices=ROLES,
        default='H'
    )
    
    REQUIRED_FIELDS = ['dni', 'telefono']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


class Alojamiento(models.Model):
    """
    Representa un establecimiento o alojamiento turístico (hotel, hostel, cabaña, etc.)
    publicado por un propietario y verificado por la administración.
    """
    # Estados de aprobacion del alojamiento
    ESTADOS = (
        ('P', 'Pendiente'),
        ('A', 'Activo'),
        ('R', 'Rechazado'),
    )
    TIPOS = (
        ('HT', 'Hotel'),
        ('HS', 'Hostel'),
        ('CA', 'Casa'),
        ('DP', 'Departamento'),
        ('CB', 'Cabana')
    )
    UBICACIONES_REALES = (
        # Costa Atlántica
        ('Mar del Plata', 'Mar del Plata (Buenos Aires)'),
        ('Mar del Tuyú', 'Mar del Tuyú (Buenos Aires)'),
        ('Pinamar', 'Pinamar (Buenos Aires)'),
        ('Villa Gesell', 'Villa Gesell (Buenos Aires)'),
        ('San Bernardo', 'San Bernardo (Buenos Aires)'),
        ('Santa Clara del Mar', 'Santa Clara del Mar (Buenos Aires)'),
        ('Cariló', 'Cariló (Buenos Aires)'),
        ('San Clemente del Tuyú', 'San Clemente del Tuyú (Buenos Aires)'),
        ('Mar de las Pampas', 'Mar de las Pampas (Buenos Aires)'),
        ('Miramar', 'Miramar (Buenos Aires)'),
        ('Necochea', 'Necochea (Buenos Aires)'),
        ('Monte Hermoso', 'Monte Hermoso (Buenos Aires)'),
        ('Las Grutas', 'Las Grutas (Río Negro)'),
        # Patagonia y Lagos
        ('Bariloche', 'Bariloche (Río Negro)'),
        ('San Martín de los Andes', 'San Martín de los Andes (Neuquén)'),
        ('Villa La Angostura', 'Villa La Angostura (Neuquén)'),
        ('El Calafate', 'El Calafate (Santa Cruz)'),
        ('El Chaltén', 'El Chaltén (Santa Cruz)'),
        ('Ushuaia', 'Ushuaia (Tierra del Fuego)'),
        ('Puerto Madryn', 'Puerto Madryn (Chubut)'),
        # Sierras y Centro
        ('Villa Carlos Paz', 'Villa Carlos Paz (Córdoba)'),
        ('Villa General Belgrano', 'Villa General Belgrano (Córdoba)'),
        ('Merlo', 'Merlo (San Luis)'),
        ('Mina Clavero', 'Mina Clavero (Córdoba)'),
        ('La Cumbrecita', 'La Cumbrecita (Córdoba)'),
        ('Tandil', 'Tandil (Buenos Aires)'),
        ('Sierra de la Ventana', 'Sierra de la Ventana (Buenos Aires)'),
        ('Capilla del Monte', 'Capilla del Monte (Córdoba)'),
        # Cuyo, Norte y Litoral
        ('Mendoza', 'Mendoza (Mendoza)'),
        ('San Rafael', 'San Rafael (Mendoza)'),
        ('Salta', 'Salta (Salta)'),
        ('Cafayate', 'Cafayate (Salta)'),
        ('Purmamarca', 'Purmamarca (Jujuy)'),
        ('Tilcara', 'Tilcara (Jujuy)'),
        ('Puerto Iguazú', 'Puerto Iguazú (Misiones)'),
        ('Colón', 'Colón (Entre Ríos)'),
        ('Federación', 'Federación (Entre Ríos)'),
        ('Gualeguaychú', 'Gualeguaychú (Entre Ríos)'),
        # Capitales y grandes centros
        ('Buenos Aires', 'Buenos Aires (CABA)'),
        ('Córdoba', 'Córdoba (Córdoba)'),
        ('Rosario', 'Rosario (Santa Fe)'),
    )
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default='HT'
    )
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        default='Mar del Plata',
        verbose_name='Ubicación / Ciudad'
    )
    direccion_completa = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Dirección completa'
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Ciudad o localidad'
    )
    provincia = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Provincia o región'
    )
    pais = models.CharField(
        max_length=100,
        blank=True,
        default='Argentina',
        verbose_name='País'
    )
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitud'
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitud'
    )
    calle = models.CharField(max_length=50, blank=True, default='')
    numero_calle = models.CharField(max_length=10, blank=True, default='')
    descripcion = models.TextField()
    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )
    estado = models.CharField(
        max_length=1,
        choices=ESTADOS,
        default='P'
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_aprobacion = models.DateTimeField(
        null=True,
        blank=True
    )
    servicios = models.ManyToManyField(
        'ServicioAlojamiento',
        blank=True,
        verbose_name='Servicios del alojamiento'
    )

    class Meta:
        verbose_name = 'Alojamiento'
        verbose_name_plural = 'Alojamientos'

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    @property
    def tiene_coordenadas(self):
        return self.latitud is not None and self.longitud is not None

    def get_direccion_display(self):
        if self.direccion_completa:
            return self.direccion_completa
        partes = [f"{self.calle} {self.numero_calle}".strip()]
        if self.ciudad:
            partes.append(self.ciudad)
        elif self.ubicacion:
            partes.append(self.ubicacion)
        if self.provincia:
            partes.append(self.provincia)
        return ", ".join([p for p in partes if p])

    def get_ubicacion_display_text(self):
        if self.ciudad and self.provincia:
            return f"{self.ciudad}, {self.provincia}"
        if self.ciudad:
            return self.ciudad
        return self.ubicacion or self.pais or "Argentina"

    def get_google_maps_url(self):
        if self.tiene_coordenadas:
            return f"https://www.google.com/maps/dir/?api=1&destination={self.latitud},{self.longitud}"
        query = f"{self.nombre}, {self.get_direccion_display()}"
        return f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"


class Habitacion(models.Model):
    """
    Representa una habitación individual perteneciente a un alojamiento determinado.
    """
    numero_habitacion = models.IntegerField()
    numero_piso = models.IntegerField()
    capacidad_maxima = models.IntegerField()
    tipo = models.CharField(max_length=20)
    precio_noche = models.IntegerField()
    disponible = models.BooleanField(
        default=True,
        help_text='Indica si la habitacion esta disponible para ser reservada. El propietario puede cambiarlo manualmente.'
    )
    fecha_desocupacion_automatica = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha en la que finaliza la reserva activa para desocupar la habitacion automaticamente.'
    )
    id_alohamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'

    def __str__(self):
        return f"Hab. {self.numero_habitacion} (Piso {self.numero_piso}) - {self.id_alohamiento.nombre}"


class Reserva(models.Model):
    """
    Registra la reserva de una habitación por parte de un huésped para un rango de fechas.
    """
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()
    estado = models.CharField(max_length=20, default='Confirmada')
    pago = models.IntegerField()
    id_alohamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"Reserva {self.id} - {self.id_alohamiento.nombre} ({self.id_usuario.username})"


class Promocion(models.Model):
    """
    Define descuentos y promociones temporales aplicables a un alojamiento.
    """
    descuento = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()
    id_alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'

    def __str__(self):
        return f"Promoción {self.descuento}% - {self.id_alojamiento.nombre}"


class Reseña(models.Model):
    """
    Calificaciones y comentarios realizados por los usuarios sobre los alojamientos.
    """
    calificacion = models.IntegerField()
    descripcion = models.TextField()
    id_alohamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'

    def __str__(self):
        return f"Reseña {self.calificacion}/5 - {self.id_usuario.username}"


class SolicitudPropietario(models.Model):
    """
    Solicitud enviada por un usuario huésped para convertirse en propietario y publicar hoteles.
    """
    ESTADOS = (
        ('P', 'Pendiente'),
        ('A', 'Aprobada'),
        ('R', 'Rechazada'),
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )
    motivo = models.TextField()
    estado = models.CharField(
        max_length=1,
        choices=ESTADOS,
        default='P'
    )
    fecha_solicitud = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Solicitud de Propietario'
        verbose_name_plural = 'Solicitudes de Propietarios'

    def __str__(self):
        return f"Solicitud de {self.usuario.username} - {self.get_estado_display()}"


class ServicioAlojamiento(models.Model):
    """
    Catálogo fijo de servicios/amenities disponibles para los alojamientos.
    Cada entrada representa un servicio con su nombre e icono SVG inline.
    """
    SERVICIOS_PREDEFINIDOS = [
        ('wifi',          'Wi-Fi',                 '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>'),
        ('estacionamiento','Estacionamiento',       '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/></svg>'),
        ('piscina',       'Piscina',                '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M2 12h20"/><path d="M2 17c1.5 0 2.5-1 4-1s2.5 1 4 1 2.5-1 4-1 2.5 1 4 1"/><path d="M2 22c1.5 0 2.5-1 4-1s2.5 1 4 1 2.5-1 4-1 2.5 1 4 1"/><circle cx="18" cy="5" r="2"/><path d="m14 5 4-2"/></svg>'),
        ('piscina_clim',  'Piscina climatizada',    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M2 12h20"/><path d="M2 17c1.5 0 2.5-1 4-1s2.5 1 4 1 2.5-1 4-1 2.5 1 4 1"/><path d="M2 22c1.5 0 2.5-1 4-1s2.5 1 4 1 2.5-1 4-1 2.5 1 4 1"/><path d="M14 8h2a2 2 0 0 0 0-4h-1"/><path d="m10 4 2 8"/></svg>'),
        ('room_service',  'Servicio de habitación', '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>'),
        ('desayuno',      'Desayuno',               '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><line x1="6" y1="2" x2="6" y2="4"/><line x1="10" y1="2" x2="10" y2="4"/><line x1="14" y1="2" x2="14" y2="4"/></svg>'),
        ('all_inclusive', 'All-inclusive',          '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M12 22C6.5 22 2 17.5 2 12S6.5 2 12 2s10 4.5 10 10-4.5 10-10 10z"/><path d="m9 12 2 2 4-4"/></svg>'),
        ('gimnasio',      'Gimnasio',               '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M6.5 6.5h11"/><path d="M6.5 17.5h11"/><path d="M3 9.5v5"/><path d="M21 9.5v5"/><path d="M6.5 6.5v11"/><path d="M17.5 6.5v11"/></svg>'),
        ('sala_juegos',   'Sala de juegos',         '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><line x1="6" y1="11" x2="10" y2="11"/><line x1="8" y1="9" x2="8" y2="13"/><line x1="15" y1="12" x2="15.01" y2="12"/><line x1="18" y1="10" x2="18.01" y2="10"/><path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59c-.006.052-.01.101-.017.152C2.604 9.416 2 14.456 2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.414-1.414A2 2 0 0 1 9.828 16h4.344a2 2 0 0 1 1.414.586L17 18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.545-.604-6.584-.685-7.258-.007-.05-.011-.1-.017-.151A4 4 0 0 0 17.32 5z"/></svg>'),
        ('casino',        'Casino',                 '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><rect x="2" y="2" width="9" height="9" rx="1"/><rect x="13" y="2" width="9" height="9" rx="1"/><rect x="2" y="13" width="9" height="9" rx="1"/><path d="m13 13 9 9"/><path d="m22 13-9 9"/></svg>'),
        ('futbol',        'Cancha de Fútbol',       '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><circle cx="12" cy="12" r="10"/><path d="m12 2 2 7h7l-5.5 4 2 7L12 16l-5.5 4 2-7L3 9h7z"/></svg>'),
        ('basquet',       'Cancha de Básquet',      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><circle cx="12" cy="12" r="10"/><path d="M4.93 4.93c4.08 4.08 6.07 8.92 5.07 14.07"/><path d="M19.07 4.93c-4.08 4.08-6.07 8.92-5.07 14.07"/><path d="M2 12h20"/></svg>'),
        ('spa',           'Spá',                    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M12 22a9.8 9.8 0 0 1-4.58-1.13A7.75 7.75 0 0 1 2 14c0-3.62 2.57-6.76 6.18-7.67A9 9 0 0 1 12 2a9 9 0 0 1 3.82.33C19.43 7.24 22 10.38 22 14a7.75 7.75 0 0 1-5.42 6.87A9.8 9.8 0 0 1 12 22z"/><path d="M12 22v-4"/><path d="M10 18h4"/></svg>'),
        ('masajes',       'Masajes',                '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M16 16c0 2.2-1.8 4-4 4H8a4 4 0 0 1 0-8h4"/><path d="M8 12c0-2.2 1.8-4 4-4h4a4 4 0 0 1 0 8"/><path d="M12 3v3"/><path d="m9.5 5.5 1 1"/><path d="m14.5 5.5-1 1"/></svg>'),
        ('jacuzzi',       'Jacuzzi',                '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M3 5.5C3 3 5 2 7 2s3 1.5 3 3-2 3-2 5c0 1.5 1 3 3 3s3-1.5 3-3-2-3.5-2-5c0-1.5 2-3 4-3"/><path d="M3 19h18"/><path d="M5 22h14"/><path d="M5 14h14v2a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4v-2z"/></svg>'),
        ('bar',           'Bar',                    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M8 22H5a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2h-3"/><path d="M11 17v-5l-3-4h8l-3 4v5"/><path d="M9 17h6"/></svg>'),
        ('cine',          'Sala de cine',           '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>'),
        ('restaurante',   'Restaurante',            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:18px;height:18px;min-width:18px;min-height:18px;display:inline-block;vertical-align:middle;"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>'),
    ]

    nombre = models.CharField(max_length=50, unique=True)
    clave = models.CharField(max_length=30, unique=True, help_text='Identificador interno')
    icono_svg = models.TextField(help_text='SVG inline del icono')
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    @classmethod
    def poblar_servicios(cls):
        """Crea o actualiza los servicios predefinidos."""
        for i, (clave, nombre, svg) in enumerate(cls.SERVICIOS_PREDEFINIDOS):
            obj, created = cls.objects.get_or_create(
                clave=clave,
                defaults={'nombre': nombre, 'icono_svg': svg, 'orden': i}
            )
            if not created:
                obj.nombre = nombre
                obj.icono_svg = svg
                obj.orden = i
                obj.save()


class ImagenAlojamiento(models.Model):
    """
    Imagen asociada a un alojamiento. Una puede ser la portada principal
    y el resto componen la galería (hasta 10 imágenes extra).
    """
    alojamiento = models.ForeignKey(
        Alojamiento,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='hoteles/', verbose_name='Imagen')
    es_principal = models.BooleanField(default=False, verbose_name='Imagen principal')
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Imagen de alojamiento'
        verbose_name_plural = 'Imágenes de alojamiento'
        ordering = ['-es_principal', 'orden']

    def __str__(self):
        tipo = 'Principal' if self.es_principal else f'Galería #{self.orden}'
        return f"{tipo} — {self.alojamiento.nombre}"
