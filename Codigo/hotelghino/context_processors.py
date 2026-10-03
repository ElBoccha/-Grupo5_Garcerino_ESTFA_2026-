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
