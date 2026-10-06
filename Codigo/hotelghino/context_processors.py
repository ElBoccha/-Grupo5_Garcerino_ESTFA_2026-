from .models import Alojamiento


def admin_pending_hotels(request):
    """
    Inyecta en el contexto la cantidad de hoteles pendientes de aprobacion.
    Solo se calcula para usuarios administradores autenticados.
    """
    if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'A':
        count = Alojamiento.objects.filter(estado='P').count()
        return {'pending_hotels_count': count}
    return {'pending_hotels_count': 0}


def carto_context(request):
    """
    Inyecta la clave de CARTO Basemaps en el contexto de todos los templates.
    Permite cargar teselas oficiales de CARTO sin marcas de agua.
    """
    from django.conf import settings
    return {
        'CARTO_API_KEY': getattr(settings, 'CARTO_API_KEY', '').strip(),
    }


def date_limits(request):
    """
    Inyecta en el contexto las fechas limite permitidas para busquedas y reservas:
    hoy como minimo y 1 ano hacia adelante como maximo.
    """
    from django.utils import timezone
    from .utils import obtener_fecha_limite_reserva

    hoy = timezone.now().date()
    max_fecha = obtener_fecha_limite_reserva(hoy)
    hoy_str = hoy.strftime('%Y-%m-%d')
    max_str = max_fecha.strftime('%Y-%m-%d')
    return {
        'hoy_str': hoy_str,
        'max_fecha_str': max_str,
        'min_fecha': hoy_str,
        'max_fecha': max_str,
    }

