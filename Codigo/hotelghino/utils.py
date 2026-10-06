from datetime import timedelta
from django.utils import timezone


def obtener_fecha_limite_reserva(base=None):
    """
    Retorna la fecha maxima permitida para busquedas y reservas
    (exactamente 1 ano hacia adelante desde la fecha base o hoy).
    Maneja anos bisiestos de forma segura (29 de febrero -> 28 de febrero).
    """
    if base is None:
        base = timezone.now().date()
    try:
        return base.replace(year=base.year + 1)
    except ValueError:
        return base.replace(year=base.year + 1, day=28)
