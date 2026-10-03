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

        # 3. Se pueden añadir habitaciones directamente mientras esté pendiente
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
        self.assertEqual(hotel.habitacion_set.count(), 1)

        # 4. Una vez aprobado por admin, se publica en home y mantiene sus habitaciones
        hotel.estado = 'A'
        hotel.save()

        home_resp_aprobado = self.client.get(reverse('home'))
        self.assertContains(home_resp_aprobado, 'Grand Hotel Test')

    def test_creacion_hotel_con_habitaciones_en_lote_y_servicios(self):
        from hotelghino.models import Alojamiento, ServicioAlojamiento, Habitacion
        ServicioAlojamiento.poblar_servicios()
        wifi = ServicioAlojamiento.objects.get(nombre='Wi-Fi')
        piscina = ServicioAlojamiento.objects.get(nombre='Piscina')

        self.client.force_login(self.propietario)
        resp = self.client.post(reverse('registro_hoteles'), {
            'nombre': 'Resort Mega Playa',
            'calle': 'Av. Maritima',
            'numero_calle': '500',
            'descripcion': 'Resort con todos los servicios y 50 habitaciones.',
            'servicios': [wifi.id, piscina.id],
            'crear_habitaciones_lote': True,
            'hab_desde': 1,
            'hab_hasta': 20,
            'numero_piso': 1,
            'tipo': 'Doble',
            'capacidad_maxima': 2,
            'precio_noche': 8500,
        })
        self.assertRedirects(resp, reverse('mis_hoteles'))

        hotel = Alojamiento.objects.get(nombre='Resort Mega Playa')
        self.assertEqual(hotel.estado, 'P')
        # Verifica que se crearon 20 habitaciones en lote
        self.assertEqual(hotel.habitacion_set.count(), 20)
        self.assertTrue(Habitacion.objects.filter(id_alohamiento=hotel, numero_habitacion=1).exists())
        self.assertTrue(Habitacion.objects.filter(id_alohamiento=hotel, numero_habitacion=20).exists())
        # Verifica que se guardaron los servicios
        self.assertEqual(hotel.servicios.count(), 2)
        self.assertTrue(hotel.servicios.filter(nombre='Wi-Fi').exists())
        self.assertTrue(hotel.servicios.filter(nombre='Piscina').exists())

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


class GeolocationLeafletTests(TestCase):
    def setUp(self):
        self.propietario = Usuario.objects.create_user(
            username='prop_geo',
            password='Password123',
            dni=55555555,
            telefono='555555555',
            rol='P'
        )
        self.huesped = Usuario.objects.create_user(
            username='huesped_geo',
            password='Password123',
            dni=66666666,
            telefono='666666666',
            rol='H'
        )

    def test_creacion_hotel_con_geolocalizacion_real(self):
        from hotelghino.models import Alojamiento
        self.client.force_login(self.propietario)

        response = self.client.post(reverse('registro_hoteles'), {
            'nombre': 'Hotel Patagónico Bariloche',
            'direccion_completa': 'Av. San Martín 450, San Carlos de Bariloche, Río Negro',
            'ciudad': 'San Carlos de Bariloche',
            'provincia': 'Río Negro',
            'pais': 'Argentina',
            'latitud': '-41.133472',
            'longitud': '-71.310278',
            'calle': 'Av. San Martín',
            'numero_calle': '450',
            'descripcion': 'Hermoso hotel de montaña con vista al lago.',
        })
        self.assertRedirects(response, reverse('mis_hoteles'))

        hotel = Alojamiento.objects.get(nombre='Hotel Patagónico Bariloche')
        self.assertTrue(hotel.tiene_coordenadas)
        self.assertAlmostEqual(float(hotel.latitud), -41.133472, places=4)
        self.assertAlmostEqual(float(hotel.longitud), -71.310278, places=4)
        self.assertEqual(hotel.ciudad, 'San Carlos de Bariloche')
        self.assertEqual(hotel.provincia, 'Río Negro')

    def test_validacion_coordenadas_invalidas(self):
        from hotelghino.forms import RegistroAlojamiento
        form_lat_invalida = RegistroAlojamiento(data={
            'nombre': 'Hotel Lat Inv',
            'latitud': '95.5',
            'longitud': '-58.38',
            'descripcion': 'Test',
        })
        self.assertFalse(form_lat_invalida.is_valid())
        self.assertIn('latitud', form_lat_invalida.errors)

        form_lng_invalida = RegistroAlojamiento(data={
            'nombre': 'Hotel Lng Inv',
            'latitud': '-34.60',
            'longitud': '-195.0',
            'descripcion': 'Test',
        })
        self.assertFalse(form_lng_invalida.is_valid())
        self.assertIn('longitud', form_lng_invalida.errors)

    def test_detalle_hotel_muestra_seccion_ubicacion_y_como_llegar(self):
        from hotelghino.models import Alojamiento
        hotel = Alojamiento.objects.create(
            nombre='Hotel Vista Panorámica',
            direccion_completa='Av. Exequiel Bustillo Km 5, Bariloche',
            ciudad='Bariloche',
            provincia='Río Negro',
            pais='Argentina',
            latitud=-41.125000,
            longitud=-71.340000,
            calle='Av. Exequiel Bustillo',
            numero_calle='5000',
            descripcion='Hotel con vista al lago Nahuel Huapi.',
            id_usuario=self.propietario,
            estado='A'
        )

        self.client.force_login(self.huesped)
        response = self.client.get(reverse('detalle_hotel', args=[hotel.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ubicación y cómo llegar')
        self.assertContains(response, 'hotel-map-view')
        self.assertContains(response, 'Cómo llegar')
        self.assertContains(response, 'https://www.google.com/maps/dir/?api=1&amp;destination=')
        self.assertContains(response, '-41.125000,-71.340000')
        self.assertContains(response, 'Bariloche')
        self.assertContains(response, 'Río Negro')

    def test_hotel_antiguo_sin_coordenadas_no_rompe_detalle(self):
        from hotelghino.models import Alojamiento
        hotel_antiguo = Alojamiento.objects.create(
            nombre='Hotel Histórico Sin Geo',
            calle='Mitre',
            numero_calle='100',
            descripcion='Hotel antiguo sin coordenadas asignadas',
            id_usuario=self.propietario,
            estado='A'
        )

        self.client.force_login(self.huesped)
        response = self.client.get(reverse('detalle_hotel', args=[hotel_antiguo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'La ubicación en el mapa de este alojamiento todavía no fue especificada')
        self.assertNotContains(response, 'hotel-map-view')

    def test_busqueda_por_ciudad_provincia_y_direccion(self):
        from hotelghino.models import Alojamiento
        Alojamiento.objects.create(
            nombre='Posada del Valle',
            direccion_completa='Ruta 40 Km 120, Cafayate, Salta',
            ciudad='Cafayate',
            provincia='Salta',
            pais='Argentina',
            latitud=-26.072222,
            longitud=-65.976111,
            descripcion='Bodega y posada en los valles calchaquíes',
            id_usuario=self.propietario,
            estado='A'
        )

        self.client.force_login(self.huesped)

        # Búsqueda por ciudad
        resp_ciudad = self.client.get(reverse('home'), {'destino': 'Cafayate'})
        self.assertContains(resp_ciudad, 'Posada del Valle')

        # Búsqueda por provincia
        resp_provincia = self.client.get(reverse('home'), {'destino': 'Salta'})
        self.assertContains(resp_provincia, 'Posada del Valle')

        # Búsqueda por término parcial con acento/sin acento
        resp_norm = self.client.get(reverse('home'), {'destino': 'cafáyate'})
        self.assertContains(resp_norm, 'Posada del Valle')

    def test_home_incluye_datos_para_mapa_general_de_resultados(self):
        from hotelghino.models import Alojamiento
        Alojamiento.objects.create(
            nombre='Hotel Mar del Plata Centro',
            ciudad='Mar del Plata',
            provincia='Buenos Aires',
            pais='Argentina',
            latitud=-38.005500,
            longitud=-57.542600,
            descripcion='Hotel en la peatonal San Martín.',
            id_usuario=self.propietario,
            estado='A'
        )

        response = self.client.get(reverse('home'), {'destino': 'Mar del Plata'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'btn-toggle-results-map')
        self.assertContains(response, 'general-results-map')
        self.assertContains(response, '-38.0055')
        self.assertContains(response, '-57.5426')

    def test_carto_context_processor_and_base_config(self):
        with self.settings(CARTO_API_KEY='cartotestkey123'):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['CARTO_API_KEY'], 'cartotestkey123')
            self.assertContains(response, 'HOTELGHINO_MAP_CONFIG')
            self.assertContains(response, 'cartotestkey123')
            self.assertContains(response, 'createCartoTileLayer')

    def test_busqueda_combinada_nombre_y_ubicacion(self):
        from hotelghino.models import Alojamiento
        Alojamiento.objects.create(
            nombre='Gran Hotel Austral',
            ciudad='Ushuaia',
            provincia='Tierra del Fuego',
            pais='Argentina',
            calle='San Martín',
            numero_calle='100',
            latitud=-54.807222,
            longitud=-68.304444,
            descripcion='Hotel en el fin del mundo.',
            id_usuario=self.propietario,
            estado='A'
        )

        # Búsqueda combinada: parte del nombre + ciudad
        resp_combinada = self.client.get(reverse('home'), {'destino': 'Gran Ushuaia'})
        self.assertContains(resp_combinada, 'Gran Hotel Austral')

        # Búsqueda con coma: ciudad + provincia
        resp_coma = self.client.get(reverse('home'), {'destino': 'Ushuaia, Tierra del Fuego'})
        self.assertContains(resp_coma, 'Gran Hotel Austral')

    def test_modificar_hotel_actualiza_coordenadas(self):
        from hotelghino.models import Alojamiento
        hotel = Alojamiento.objects.create(
            nombre='Hotel Original',
            ciudad='Córdoba',
            provincia='Córdoba',
            latitud=-31.420083,
            longitud=-64.188776,
            descripcion='Original',
            id_usuario=self.propietario,
            estado='A'
        )

        self.client.force_login(self.propietario)
        resp_post = self.client.post(reverse('modificar_hotel', args=[hotel.id]), {
            'nombre': 'Hotel Original Actualizado',
            'direccion_completa': 'Av. Colón 500, Córdoba',
            'ciudad': 'Córdoba Capital',
            'provincia': 'Córdoba',
            'pais': 'Argentina',
            'calle': 'Av. Colón',
            'numero_calle': '500',
            'latitud': '-31.415000',
            'longitud': '-64.190000',
            'descripcion': 'Actualizado con nuevas coordenadas.',
        })
        self.assertRedirects(resp_post, reverse('mis_hoteles'))

        hotel.refresh_from_db()
        self.assertEqual(hotel.nombre, 'Hotel Original Actualizado')
        self.assertAlmostEqual(float(hotel.latitud), -31.415000, places=4)
        self.assertAlmostEqual(float(hotel.longitud), -64.190000, places=4)
        self.assertEqual(hotel.ciudad, 'Córdoba Capital')

    def test_admin_alojamientos_changelist_con_y_sin_coordenadas(self):
        from hotelghino.models import Alojamiento
        admin_user = Usuario.objects.create_superuser(
            username='super_admin',
            email='admin@test.com',
            password='AdminPassword123',
            dni=12312312,
            telefono='12345678',
            rol='A'
        )
        # Hotel con coordenadas
        Alojamiento.objects.create(
            nombre='Hotel Con Geo',
            latitud=-34.60,
            longitud=-58.38,
            id_usuario=self.propietario,
            estado='P'
        )
        # Hotel sin coordenadas (el que disparaba format_html sin args)
        Alojamiento.objects.create(
            nombre='Hotel Sin Geo',
            latitud=None,
            longitud=None,
            id_usuario=self.propietario,
            estado='P'
        )

        self.client.force_login(admin_user)
        response = self.client.get('/admin/hotelghino/alojamiento/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hotel Con Geo')
        self.assertContains(response, 'Hotel Sin Geo')
        self.assertContains(response, 'Sin fijar')

    def test_servir_archivos_media_en_produccion(self):
        import os
        from django.conf import settings

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        test_file_path = os.path.join(settings.MEDIA_ROOT, 'test_media_render.txt')
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write('test-media-content')

        response = None
        try:
            response = self.client.get('/media/test_media_render.txt')
            self.assertEqual(response.status_code, 200)
            content = b''.join(response.streaming_content).decode('utf-8')
            self.assertEqual(content, 'test-media-content')
        finally:
            if response is not None:
                response.close()
            if os.path.exists(test_file_path):
                os.remove(test_file_path)




