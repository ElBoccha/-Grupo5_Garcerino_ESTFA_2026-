from django.test import TestCase
from django.contrib.auth import get_user_model
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
