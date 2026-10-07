from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generador de tokens criptográficamente seguros para la verificación de correo.
    Incluye en el hash el estado de email_verificado y el email del usuario para que
    el token quede inmediatamente invalidado una vez que la cuenta ha sido verificada
    o si la dirección de correo cambia.
    """
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.is_active}{user.email_verificado}{user.email}{timestamp}"


email_verification_token_generator = EmailVerificationTokenGenerator()


def enviar_email_verificacion(request, usuario):
    """
    Genera el enlace con UID y token y despacha el correo de verificación vía Brevo SMTP.
    Devuelve (True, None) si el envío fue exitoso o (False, mensaje_error) si ocurrió una falla.
    """
    if not usuario.email:
        return False, "El usuario no posee una dirección de correo electrónico registrada."

    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = email_verification_token_generator.make_token(usuario)

    if request is not None:
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
    else:
        protocol = 'https'
        domain = 'hotelghino.onrender.com'

    verification_url = f"{protocol}://{domain}/verificar-email/{uid}/{token}/"

    context = {
        'user': usuario,
        'uid': uid,
        'token': token,
        'protocol': protocol,
        'domain': domain,
        'verification_url': verification_url,
    }

    try:
        html_message = render_to_string('verificar_email_mensaje.html', context)
        plain_message = (
            f"Hola {usuario.username},\n\n"
            f"Gracias por crear tu cuenta en Hotelghino. Para activarla y poder iniciar sesión, "
            f"por favor confirmá tu correo electrónico ingresando al siguiente enlace:\n\n"
            f"{verification_url}\n\n"
            f"Este enlace es de uso único y temporal por razones de seguridad.\n\n"
            f"Si no creaste una cuenta en Hotelghino, podés desestimar este mensaje.\n\n"
            f"Saludos cordiales,\n"
            f"El equipo de Hotelghino"
        )

        send_mail(
            subject='Verificá tu correo electrónico - Hotelghino',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, None
    except Exception as e:
        logger.exception("Error al enviar el email de verificación vía Brevo SMTP: %s", e)
        return False, str(e)
