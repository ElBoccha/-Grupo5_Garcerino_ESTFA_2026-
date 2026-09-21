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

    def test_propietario_registra_hotel_y_flujo_aprobacion(self):
        from hotelghino.models import Alojamiento
        self.client.force_login(self.propietario)
        response = self.client.post(reverse('registro_hoteles'), {
            'nombre': 'Grand Hotel Test',
            'calle': 'Av. Principal',
            'numero_calle': '123',
            'descripcion': 'Un hotel excelente cerca de la playa.',
        })
        self.assertRedirects(response, reverse('mis_hoteles'))

        hotel = Alojamiento.objects.get(nombre='Grand Hotel Test')
        # 1. El hotel nuevo queda en estado pendiente
        self.assertEqual(hotel.estado, 'P')

        # 2. No aparece publicado en home mientras esté pendiente
        self.client.force_login(self.huesped)
        home_resp = self.client.get(reverse('home'))
        self.assertNotContains(home_resp, 'Grand Hotel Test')

        # 3. No se pueden añadir habitaciones mientras esté pendiente
        self.client.force_login(self.propietario)
        resp_hab = self.client.post(reverse('registrar_habitacion', args=[hotel.id]), {
            'numero_habitacion': 101,
            'numero_piso': 1,
            'capacidad_maxima': 2,
            'tipo': 'Simple',
            'precio_noche': 3000,
            'disponible': True,
        })
        self.assertRedirects(resp_hab, reverse('mis_hoteles'))
        self.assertEqual(hotel.habitacion_set.count(), 0)

        # 4. Una vez aprobado por admin, se publica en home y permite añadir habitaciones
        hotel.estado = 'A'
        hotel.save()

        home_resp_aprobado = self.client.get(reverse('home'))
        self.assertContains(home_resp_aprobado, 'Grand Hotel Test')

        resp_hab_ok = self.client.post(reverse('registrar_habitacion', args=[hotel.id]), {
            'numero_habitacion': 101,
            'numero_piso': 1,
            'capacidad_maxima': 2,
            'tipo': 'Simple',
            'precio_noche': 3000,
            'disponible': True,
        })
        self.assertRedirects(resp_hab_ok, reverse('mis_hoteles'))
        self.assertEqual(hotel.habitacion_set.count(), 1)

    def test_vista_invitado_home_y_redireccion_login_al_reservar(self):
        from hotelghino.models import Alojamiento
        hotel = Alojamiento.objects.create(
            nombre='Hotel para Invitados',
            calle='Costanera',
            numero_calle='100',
            descripcion='Hotel frente al mar',
            id_usuario=self.propietario,
            estado='A'
        )
        # El invitado puede ver home accediendo a la ruta raíz '/' por defecto
        self.client.logout()
        response_root = self.client.get('/')
        self.assertEqual(response_root.status_code, 200)
        self.assertContains(response_root, 'Hotel para Invitados')
        self.assertContains(response_root, 'Ingresar')
        self.assertContains(response_root, f"/login/?next=/hoteles/{hotel.id}/")

        # Acceder a '/home/' también funciona
        response_home = self.client.get('/home/')
        self.assertEqual(response_home.status_code, 200)

        # Al intentar ingresar a detalle del hotel sin login, redirige al login
        resp_detalle = self.client.get(reverse('detalle_hotel', args=[hotel.id]))
        self.assertEqual(resp_detalle.status_code, 302)
        self.assertTrue(resp_detalle.url.startswith('/login/?next='))

    def test_admin_ve_notificacion_de_hoteles_pendientes(self):
        from hotelghino.models import Alojamiento, Usuario
        admin_user = Usuario.objects.create_user(
            username='adminuser',
            email='admin@test.com',
            password='Password123',
            dni=99999999,
            telefono='99999999',
            rol='A'
        )
        Alojamiento.objects.create(
            nombre='Hotel Pendiente Admin',
            calle='Calle 1',
            numero_calle='10',
            descripcion='Pendiente de aprobacion',
            id_usuario=self.propietario,
            estado='P'
        )
        self.client.force_login(admin_user)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Tenés <strong>1</strong> hotel(es) pendiente(s) de aprobación.')

    def test_busqueda_hotel_por_destino(self):
        from hotelghino.models import Alojamiento
        Alojamiento.objects.create(
            nombre='Beto cincelados',
            calle='Andrade',
            numero_calle='271',
            descripcion='beto estas de buen humor: no se',
            id_usuario=self.propietario,
            estado='A'
        )
        self.client.force_login(self.huesped)
        response = self.client.get(reverse('home'), {'destino': 'Beto'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beto cincelados')

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


class PasswordResetTests(TestCase):
    def setUp(self):
        from django.core import mail
        self.user = Usuario.objects.create_user(
            username='usuarioprueba',
            email='test@hotelghino.com',
            password='ClaveVieja123',
            dni=44556677,
            telefono='1155443322'
        )

    def test_login_page_contiene_enlace_recuperar_contrasena(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('password_reset'))
        self.assertContains(response, '¿Olvidaste tu contraseña?')

    def test_solicitud_recuperar_contrasena_genera_enlace(self):
        """La vista custom renderiza el reset_link en la misma pagina (sin SMTP configurado en tests)"""
        response = self.client.post(reverse('password_reset'), {
            'email': 'test@hotelghino.com'
        })
        self.assertEqual(response.status_code, 200)
        # La vista custom devuelve la misma pagina con el enlace o mensaje de exito
        self.assertContains(response, 'recuperar-contrasena/restablecer/')

    def test_flujo_completo_cambio_de_contrasena(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        # Acceder a la URL de confirmación (Django redirige internamente a 'set-password' para proteger el token en sesión)
        confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(confirm_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nueva contraseña')

        # Obtener la URL donde se renderiza el formulario (con token protegido en sesión)
        form_action_url = response.redirect_chain[-1][0] if response.redirect_chain else confirm_url

        # Enviar la nueva contraseña
        post_response = self.client.post(form_action_url, {
            'new_password1': 'NuevaClaveSuperSegura123!',
            'new_password2': 'NuevaClaveSuperSegura123!',
        })
        self.assertRedirects(post_response, reverse('password_reset_complete'))

        # Verificar que la nueva contraseña funciona en el login
        login_response = self.client.post(reverse('login'), {
            'username': 'usuarioprueba',
            'password': 'NuevaClaveSuperSegura123!'
        })
        self.assertRedirects(login_response, reverse('home'))

