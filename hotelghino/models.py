from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Usuario(AbstractUser):
    dni = models.IntegerField()
    telefono = models.CharField(max_length = 15)


class Alojamiento(models.Model):
    nombre = models.CharField(max_length = 50)
    tipo = models.CharField(max_length = 20)
    calle = models.CharField(max_length = 50)
    numero_calle = models.CharField(max_length = 10)
    descripcion = models.CharField(max_length = 1000)
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)


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
    descripción = models.CharField(max_length = 1000)
    id_alohamiento = models.ForeignKey(Alojamiento, on_delete = models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete = models.CASCADE)






