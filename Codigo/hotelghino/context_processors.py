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
