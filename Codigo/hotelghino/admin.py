from django.contrib import admin
from .models import Alojamiento
from .models import Habitacion
from .models import Promocion

# Register your models here.

admin.site.register(Alojamiento)
admin.site.register(Habitacion)
admin.site.register(Promocion)