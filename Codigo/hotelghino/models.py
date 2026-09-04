from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


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
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default='HT'
    )
    calle = models.CharField(max_length=50)
    numero_calle = models.CharField(max_length=10)
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

    class Meta:
        verbose_name = 'Alojamiento'
        verbose_name_plural = 'Alojamientos'

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Habitacion(models.Model):
    """
    Representa una habitación individual perteneciente a un alojamiento determinado.
    """
    numero_habitacion = models.IntegerField()
    numero_piso = models.IntegerField()
    capacidad_maxima = models.IntegerField()
    tipo = models.CharField(max_length=20)
    precio_noche = models.IntegerField()
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
