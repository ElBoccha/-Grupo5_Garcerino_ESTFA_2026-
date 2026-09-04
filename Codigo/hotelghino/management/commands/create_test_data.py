from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hotelghino.models import SolicitudPropietario, Alojamiento

Usuario = get_user_model()

class Command(BaseCommand):
    help = 'Crea datos de prueba: usuarios y hoteles'

    def handle(self, *args, **options):
        user, created = Usuario.objects.get_or_create(
            username='propietario_prueba',
            defaults={
                'email': 'propietario_prueba@example.com',
                'dni': 12345678,
                'telefono': '123456789',
                'rol': 'P',
                'is_staff': True,
            }
        )
        if created:
            user.set_password('1234')
            user.save()
            self.stdout.write(self.style.SUCCESS('Usuario de prueba creado.'))
        else:
            self.stdout.write(self.style.WARNING('Usuario de prueba ya existía.'))

        solicitudes = [
            {
                'motivo': 'Quiero publicar mi alojamiento en la plataforma.',
                'estado': 'P',
            },
            {
                'motivo': 'Necesito acceso para administrar mi hotel.',
                'estado': 'P',
            },
            {
                'motivo': 'Solicito revisar mi documentación como propietario.',
                'estado': 'A',
            }
        ]

        for data in solicitudes:
            solicitud, created = SolicitudPropietario.objects.get_or_create(
                usuario=user,
                motivo=data['motivo'],
                defaults={'estado': data['estado']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Solicitud creada: {solicitud.motivo[:50]}'))

        # Hotel Beto cincelados
        h1, created1 = Alojamiento.objects.get_or_create(
            nombre='Beto cincelados',
            defaults={
                'tipo': 'HT',
                'calle': 'Andrade',
                'numero_calle': '271',
                'descripcion': 'beto estas de buen humor: no se',
                'id_usuario': user,
                'estado': 'P'
            }
        )
        if created1:
            self.stdout.write(self.style.SUCCESS('Hotel Beto cincelados creado.'))

        # Hotel Sorro
        h2, created2 = Alojamiento.objects.get_or_create(
            nombre='Sorro',
            defaults={
                'tipo': 'HT',
                'calle': 'LAG TIO',
                'numero_calle': '676767',
                'descripcion': 'Sorro',
                'id_usuario': user,
                'estado': 'P'
            }
        )
        if created2:
            self.stdout.write(self.style.SUCCESS('Hotel Sorro creado.'))

        self.stdout.write(self.style.SUCCESS('Datos de prueba creados exitosamente.'))
