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
