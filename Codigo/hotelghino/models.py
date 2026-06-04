from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.

class Usuario(AbstractUser):
    dni = models.IntegerField()
    telefono = models.CharField(max_length = 15)
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


class Alojamiento(models.Model):
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
    nombre = models.CharField(max_length = 50)
    tipo = models.CharField(max_length = 20)
    calle = models.CharField(
        max_length = 50,
        choices=TIPOS,
        default='HT'
    )
    numero_calle = models.CharField(max_length = 10)
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
    fecha_creacion = models.DateTimeField(default=datetime.now)
    fecha_aprobacion = models.DateTimeField(
    null=True,
    blank=True
    )


class Habitacion(models.Model):
    numero_habitacion = models.IntegerField()
    numero_piso = models.IntegerField()
    capacidad_maxima = models.IntegerField()
    tipo = models.CharField(max_length = 20)
    precio_noche = models.IntegerField()
    id_alohamiento = models.ForeignKey(Alojamiento, on_delete = models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)


class Reserva(models.Model):
    fecha_inico = models.DateField()
    fecha_finalización = models.DateField()
    estado = models.CharField(max_length = 20)
    pago = models.IntegerField()
    id_alohamiento = models.ForeignKey(Alojamiento, on_delete = models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)
    id_habitacion = models.ForeignKey(Habitacion, on_delete = models.CASCADE)
   

class Promocion(models.Model):
    descuento = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()
    id_alojamiento = models.ForeignKey(Alojamiento, on_delete = models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)


class Reseña(models.Model):
    calificacion = models.IntegerField()
    descripción = models.TextField()
    id_alohamiento = models.ForeignKey(Alojamiento, on_delete = models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)

class SolicitudPropietario(models.Model):

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
        auto_now_add=True
    )






