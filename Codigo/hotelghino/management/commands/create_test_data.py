from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hotelghino.models import SolicitudPropietario, Alojamiento, Habitacion

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

        # Gran Hotel Mar del Tuyu
        h3, created3 = Alojamiento.objects.get_or_create(
            nombre='Gran Hotel Mar del Tuyu',
            defaults={
                'tipo': 'HT',
                'ubicacion': 'Mar del Tuyú',
                'descripcion': 'Gran hotel frente al mar con todas las comodidades.',
                'id_usuario': user,
                'estado': 'A',
            }
        )
        if created3:
            self.stdout.write(self.style.SUCCESS('Gran Hotel Mar del Tuyu creado.'))

        habitaciones_h3 = [
            {'numero_habitacion': 101, 'numero_piso': 1, 'tipo': 'Simple',           'capacidad_maxima': 1, 'camas': '1 cama individual',                      'precio_noche': 8500,  'descripcion': 'Habitación simple con vista al jardín'},
            {'numero_habitacion': 102, 'numero_piso': 1, 'tipo': 'Doble Vista al Mar','capacidad_maxima': 2, 'camas': '1 cama matrimonial',                     'precio_noche': 14000, 'descripcion': 'Habitación doble con vista al mar'},
            {'numero_habitacion': 103, 'numero_piso': 1, 'tipo': 'Matrimonial',      'capacidad_maxima': 2, 'camas': '1 cama matrimonial',                      'precio_noche': 12000, 'descripcion': 'Habitación matrimonial confortable'},
            {'numero_habitacion': 201, 'numero_piso': 2, 'tipo': 'Triple',           'capacidad_maxima': 3, 'camas': '1 cama matrimonial + 1 cama individual',  'precio_noche': 18000, 'descripcion': 'Habitación triple con balcón'},
            {'numero_habitacion': 202, 'numero_piso': 2, 'tipo': 'Suite',            'capacidad_maxima': 4, 'camas': '2 camas matrimoniales',                   'precio_noche': 28000, 'descripcion': 'Suite con jacuzzi y vista panorámica al mar'},
        ]
        for hab_data in habitaciones_h3:
            hab, hab_created = Habitacion.objects.get_or_create(
                numero_habitacion=hab_data['numero_habitacion'],
                id_alohamiento=h3,
                defaults={
                    'numero_piso':      hab_data['numero_piso'],
                    'tipo':             hab_data['tipo'],
                    'capacidad_maxima': hab_data['capacidad_maxima'],
                    'camas':            hab_data['camas'],
                    'precio_noche':     hab_data['precio_noche'],
                    'descripcion':      hab_data['descripcion'],
                    'disponible':       True,
                    'id_usuario':       user,
                }
            )
            if hab_created:
                self.stdout.write(self.style.SUCCESS(f'  Hab {hab_data["numero_habitacion"]} (Gran Hotel Mar del Tuyu) creada.'))

        # Hosteria Santa Clara
        h4, created4 = Alojamiento.objects.get_or_create(
            nombre='Hosteria Santa Clara',
            defaults={
                'tipo': 'HT',
                'ubicacion': 'Santa Clara del Mar',
                'descripcion': 'Hostería familiar en Santa Clara del Mar.',
                'id_usuario': user,
                'estado': 'A',
            }
        )
        if created4:
            self.stdout.write(self.style.SUCCESS('Hosteria Santa Clara creada.'))

        habitaciones_h4 = [
            {'numero_habitacion': 1, 'numero_piso': 0, 'tipo': 'Simple',       'capacidad_maxima': 1, 'camas': '1 cama individual',                     'precio_noche': 6500,  'descripcion': 'Habitación simple con baño privado'},
            {'numero_habitacion': 2, 'numero_piso': 0, 'tipo': 'Doble',        'capacidad_maxima': 2, 'camas': '1 cama matrimonial',                    'precio_noche': 11000, 'descripcion': 'Habitación doble clásica'},
            {'numero_habitacion': 3, 'numero_piso': 0, 'tipo': 'Twin',         'capacidad_maxima': 2, 'camas': '2 camas individuales',                  'precio_noche': 11000, 'descripcion': 'Habitación twin con dos camas individuales'},
            {'numero_habitacion': 4, 'numero_piso': 1, 'tipo': 'Triple',       'capacidad_maxima': 3, 'camas': '1 cama matrimonial + 1 cama individual', 'precio_noche': 15000, 'descripcion': 'Habitación triple familiar'},
            {'numero_habitacion': 5, 'numero_piso': 1, 'tipo': 'Suite junior', 'capacidad_maxima': 2, 'camas': '1 cama king',                           'precio_noche': 20000, 'descripcion': 'Suite junior con sala de estar'},
        ]
        for hab_data in habitaciones_h4:
            hab, hab_created = Habitacion.objects.get_or_create(
                numero_habitacion=hab_data['numero_habitacion'],
                id_alohamiento=h4,
                defaults={
                    'numero_piso':      hab_data['numero_piso'],
                    'tipo':             hab_data['tipo'],
                    'capacidad_maxima': hab_data['capacidad_maxima'],
                    'camas':            hab_data['camas'],
                    'precio_noche':     hab_data['precio_noche'],
                    'descripcion':      hab_data['descripcion'],
                    'disponible':       True,
                    'id_usuario':       user,
                }
            )
            if hab_created:
                self.stdout.write(self.style.SUCCESS(f'  Hab {hab_data["numero_habitacion"]} (Hosteria Santa Clara) creada.'))

        # Hotel Casino & Spa
        h5, created5 = Alojamiento.objects.get_or_create(
            nombre='Hotel Casino & Spa',
            defaults={
                'tipo': 'HT',
                'ubicacion': 'Mar del Plata',
                'descripcion': 'Hotel de lujo con casino y spa en Mar del Plata.',
                'id_usuario': user,
                'estado': 'A',
            }
        )
        if created5:
            self.stdout.write(self.style.SUCCESS('Hotel Casino & Spa creado.'))

        habitaciones_h5 = [
            {'numero_habitacion': 101, 'numero_piso': 1, 'tipo': 'Doble Standard',      'capacidad_maxima': 2, 'camas': '1 cama matrimonial', 'precio_noche': 16000, 'descripcion': 'Habitación doble estándar'},
            {'numero_habitacion': 102, 'numero_piso': 1, 'tipo': 'Doble Vista al Mar',  'capacidad_maxima': 2, 'camas': '1 cama matrimonial', 'precio_noche': 22000, 'descripcion': 'Habitación doble con vista al mar'},
            {'numero_habitacion': 201, 'numero_piso': 2, 'tipo': 'Suite Spa',           'capacidad_maxima': 2, 'camas': '1 cama king',         'precio_noche': 35000, 'descripcion': 'Suite con acceso al spa y bañera de hidromasaje'},
            {'numero_habitacion': 202, 'numero_piso': 2, 'tipo': 'Suite Familiar',      'capacidad_maxima': 4, 'camas': '2 camas matrimoniales','precio_noche': 42000, 'descripcion': 'Suite familiar con living y cocina'},
            {'numero_habitacion': 301, 'numero_piso': 3, 'tipo': 'Suite Presidencial',  'capacidad_maxima': 2, 'camas': '1 cama king',         'precio_noche': 65000, 'descripcion': 'Suite presidencial con terraza y vista panorámica'},
        ]
        for hab_data in habitaciones_h5:
            hab, hab_created = Habitacion.objects.get_or_create(
                numero_habitacion=hab_data['numero_habitacion'],
                id_alohamiento=h5,
                defaults={
                    'numero_piso':      hab_data['numero_piso'],
                    'tipo':             hab_data['tipo'],
                    'capacidad_maxima': hab_data['capacidad_maxima'],
                    'camas':            hab_data['camas'],
                    'precio_noche':     hab_data['precio_noche'],
                    'descripcion':      hab_data['descripcion'],
                    'disponible':       True,
                    'id_usuario':       user,
                }
            )
            if hab_created:
                self.stdout.write(self.style.SUCCESS(f'  Hab {hab_data["numero_habitacion"]} (Hotel Casino & Spa) creada.'))

        self.stdout.write(self.style.SUCCESS('Datos de prueba creados exitosamente.'))
