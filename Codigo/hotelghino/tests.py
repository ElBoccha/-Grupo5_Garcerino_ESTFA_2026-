from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from hotelghino.models import SolicitudPropietario

Usuario = get_user_model()

class SolicitudPropietarioTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='propietario1',
            password='1234',
            dni=12345678,
            telefono='123456789',
            rol='P'
        )

    def test_crear_solicitud_propietario(self):
        solicitud = SolicitudPropietario.objects.create(
            usuario=self.user,
            motivo='Solicitud de prueba'
        )
        self.assertEqual(solicitud.estado, 'P')
        self.assertEqual(solicitud.usuario, self.user)
        self.assertTrue(solicitud.fecha_solicitud)


class UsuarioViewsTest(TestCase):
    def test_registro_crea_usuario_y_redirige_al_login(self):
        response = self.client.post(reverse('registro'), {
            'username': 'usuario_nuevo',
            'email': 'nuevo@example.com',
            'dni': 12345678,
            'telefono': '1122334455',
            'password1': 'ClaveSegura12345',
            'password2': 'ClaveSegura12345',
        })

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(Usuario.objects.filter(username='usuario_nuevo').exists())

    def test_modificar_usuario_actualiza_datos_y_redirige_al_home(self):
        usuario = Usuario.objects.create_user(
            username='usuario_actual',
            email='actual@example.com',
            password='ClaveSegura12345',
            dni=12345678,
            telefono='1122334455'
        )
        self.client.force_login(usuario)

        response = self.client.post(reverse('modificar_usuario'), {
            'username': 'usuario_editado',
            'email': 'editado@example.com',
            'dni': 87654321,
            'telefono': '1199887766',
            'password1': '',
            'password2': '',
        })

        usuario.refresh_from_db()
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(usuario.username, 'usuario_editado')
        self.assertEqual(usuario.email, 'editado@example.com')
        self.assertEqual(usuario.dni, 87654321)
        self.assertEqual(usuario.telefono, '1199887766')


class HotelReservaViewsTest(TestCase):
    def setUp(self):
        self.propietario = Usuario.objects.create_user(
            username='prop1',
            password='Password123',
            dni=11111111,
            telefono='111111111',
            rol='P'
        )
        self.huesped = Usuario.objects.create_user(
            username='huesped1',
            password='Password123',
            dni=22222222,
            telefono='222222222',
            rol='H'
        )

    def test_propietario_registra_hotel_y_aparece_en_home(self):
        self.client.force_login(self.propietario)
        response = self.client.post(reverse('registro_hoteles'), {
            'nombre': 'Grand Hotel Test',
            'calle': 'Av. Principal',
            'numero_calle': '123',
            'descripcion': 'Un hotel excelente cerca de la playa.',
        })
        self.assertRedirects(response, reverse('mis_hoteles'))

        # Verificar que aparece en home
        self.client.force_login(self.huesped)
        home_resp = self.client.get(reverse('home'))
        self.assertContains(home_resp, 'Grand Hotel Test')

    def test_reserva_hotel_y_ver_en_mis_reservas(self):
        # Crear hotel y habitacion
        from hotelghino.models import Alojamiento, Habitacion, Reserva
        from datetime import date, timedelta

        hotel = Alojamiento.objects.create(
            nombre='Hotel Plaza',
            calle='Calle Sol',
            numero_calle='456',
            descripcion='Hotel céntrico',
            id_usuario=self.propietario,
            estado='A'
        )
        hab = Habitacion.objects.create(
            numero_habitacion=101,
            numero_piso=1,
            capacidad_maxima=2,
            tipo='Doble',
            precio_noche=5000,
            id_alohamiento=hotel,
            id_usuario=self.propietario
        )

        self.client.force_login(self.huesped)
        today = date.today()
        d_inicio = today + timedelta(days=5)
        d_fin = today + timedelta(days=8)

        response = self.client.post(reverse('detalle_hotel', args=[hotel.id]), {
            'id_habitacion': hab.id,
            'fecha_inicio': d_inicio.strftime('%Y-%m-%d'),
            'fecha_finalizacion': d_fin.strftime('%Y-%m-%d'),
        })

        self.assertRedirects(response, reverse('mis_reservas'))
        self.assertTrue(Reserva.objects.filter(id_usuario=self.huesped, id_alohamiento=hotel).exists())

        mis_res = self.client.get(reverse('mis_reservas'))
        self.assertContains(mis_res, 'Hotel Plaza')
        self.assertContains(mis_res, 'N° 101')

