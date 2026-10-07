import os
import logging
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings

logger = logging.getLogger('hotelghino.emails')


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


def enmascarar_email(email):
    """Oculta parte del correo para preservar privacidad en los logs."""
    if not email or '@' not in email:
        return '***'
    user_part, domain_part = email.split('@', 1)
    if len(user_part) <= 2:
        masked_user = user_part[0] + '*'
    else:
        masked_user = user_part[0] + '*' * (len(user_part) - 2) + user_part[-1]
    return f"{masked_user}@{domain_part}"


def diagnosticar_error_smtp(error_str):
    """Analiza la excepción devuelta por el servidor SMTP y devuelve un diagnóstico en español."""
    if '535' in error_str or 'authentication failed' in error_str.lower():
        return (
            "Error de autenticación SMTP (535): Brevo rechazó las credenciales. "
            "Recordá que la contraseña SMTP NO es la clave con la que iniciás sesión en la web de Brevo, "
            "sino una 'Clave SMTP' (que empieza con 'xsmtpsib-...') generada en Brevo > SMTP y API > pestaña SMTP."
        )
    elif '550' in error_str or 'sender' in error_str.lower() or '451' in error_str:
        return (
            f"Remitente no autorizado en Brevo: Brevo rechazó '{settings.DEFAULT_FROM_EMAIL}'. "
            "Brevo exige que DEFAULT_FROM_EMAIL sea una dirección de correo verificada como remitente "
            "(por ejemplo, el email con el que creaste tu cuenta de Brevo)."
        )
    elif 'timed out' in error_str.lower() or 'timeout' in error_str.lower() or 'refused' in error_str.lower():
        return (
            f"Tiempo de espera agotado al conectar a {getattr(settings, 'EMAIL_HOST', 'smtp-relay.brevo.com')}:{getattr(settings, 'EMAIL_PORT', 587)}. "
            "Si tu proveedor o red bloquea el puerto 587, podés configurar BREVO_SMTP_PORT=2525 en tu archivo .env."
        )
    return None


def construir_url_verificacion(request, uid, token):
    """
    Construye la URL absoluta de verificación tanto para entorno local como producción.
    En local genera http://127.0.0.1:8000/...
    En producción (detrás del proxy de Render) genera https://<dominio>/...
    """
    path = reverse('verificar_email', kwargs={'uidb64': uid, 'token': token})
    if request is not None:
        try:
            return request.build_absolute_uri(path)
        except Exception:
            protocol = 'https' if request.is_secure() else 'http'
            domain = request.get_host()
            return f"{protocol}://{domain}{path}"
    else:
        render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        domain = render_host or '127.0.0.1:8000'
        protocol = 'https' if render_host else 'http'
        return f"{protocol}://{domain}{path}"


def enviar_email_verificacion(request, usuario):
    """
    Genera el enlace con UID y token y despacha el correo de verificación vía Brevo SMTP.
    Devuelve (True, None) si el envío fue exitoso o (False, mensaje_error) si ocurrió una falla.
    """
    if not usuario.email:
        msg = "El usuario no posee una dirección de correo electrónico registrada."
        logger.warning("Intento de envío de verificación cancelado: %s", msg)
        return False, msg

    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = email_verification_token_generator.make_token(usuario)
    verification_url = construir_url_verificacion(request, uid, token)

    context = {
        'user': usuario,
        'uid': uid,
        'token': token,
        'verification_url': verification_url,
    }

    masked = enmascarar_email(usuario.email)
    logger.info(
        "Intentando enviar email de verificación a %s [backend: %s, host: %s:%s, remitente: %s]",
        masked,
        settings.EMAIL_BACKEND,
        getattr(settings, 'EMAIL_HOST', 'n/a'),
        getattr(settings, 'EMAIL_PORT', 'n/a'),
        settings.DEFAULT_FROM_EMAIL
    )

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
        logger.info("Email de verificación enviado con éxito a %s", masked)
        return True, None

    except Exception as e:
        error_str = str(e)
        diagnostico = diagnosticar_error_smtp(error_str)
        logger.error(
            "Fallo al enviar correo de verificación a %s: %s %s",
            masked,
            error_str,
            f"| DIAGNÓSTICO: {diagnostico}" if diagnostico else ""
        )
        mensaje_salida = diagnostico if diagnostico else f"Error al conectar con el servidor de correo ({error_str})"
        return False, mensaje_salida
