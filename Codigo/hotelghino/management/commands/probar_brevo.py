from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from django.conf import settings
from hotelghino.emails import diagnosticar_error_smtp, enmascarar_email
import smtplib


class Command(BaseCommand):
    help = "Verifica la configuración y conectividad con Brevo SMTP, y opcionalmente envía un email de prueba."

    def add_arguments(self, parser):
        parser.add_argument(
            'destinatario',
            nargs='?',
            type=str,
            help='Dirección de email a la que enviar el correo de prueba (opcional)'
        )

    def handle(self, *args, **options):
        destinatario = options.get('destinatario')

        self.stdout.write(self.style.MIGRATE_HEADING("=== DIAGNÓSTICO DE CONFIGURACIÓN BREVO SMTP ==="))
        self.stdout.write(f"EMAIL_BACKEND:       {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST:          {getattr(settings, 'EMAIL_HOST', 'No configurado')}")
        self.stdout.write(f"EMAIL_PORT:          {getattr(settings, 'EMAIL_PORT', 'No configurado')}")
        self.stdout.write(f"EMAIL_USE_TLS:       {getattr(settings, 'EMAIL_USE_TLS', 'No configurado')}")
        self.stdout.write(f"EMAIL_HOST_USER:     {getattr(settings, 'EMAIL_HOST_USER', 'No configurado')}")
        
        has_pass = bool(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {'Configurada (***)' if has_pass else self.style.ERROR('NO CONFIGURADA')}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL:  {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write("")

        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(self.style.WARNING(
                "[AVISO] Actualmente el backend está en modo consola (console.EmailBackend).\n"
                "Para probar el envío real vía Brevo, asegurate de tener BREVO_SMTP_USERNAME y BREVO_SMTP_PASSWORD en tu .env"
            ))
            return

        self.stdout.write("1. Probando conexión y autenticación SMTP...")
        try:
            connection = get_connection(fail_silently=False)
            connection.open()
            self.stdout.write(self.style.SUCCESS("[OK] Conexión y autenticación con Brevo SMTP exitosas."))
            connection.close()
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(f"[ERROR 535] Falló la autenticación: {e}"))
            self.stdout.write(self.style.NOTICE(
                "-> Causa: La contraseña en BREVO_SMTP_PASSWORD no es válida.\n"
                "-> Solución: En Brevo, la contraseña SMTP NO es tu contraseña web de inicio de sesión.\n"
                "   Debés generar una 'Clave SMTP' (comienza con xsmtpsib-...) en: https://app.brevo.com/settings/keys/smtp\n"
                "   y pegarla en BREVO_SMTP_PASSWORD dentro de tu archivo .env."
            ))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] No se pudo conectar: {e}"))
            diag = diagnosticar_error_smtp(str(e))
            if diag:
                self.stdout.write(self.style.NOTICE(f"-> {diag}"))
            return

        if destinatario:
            self.stdout.write(f"\n2. Enviando correo de prueba a {destinatario}...")
            try:
                send_mail(
                    subject='Prueba de envío - Hotelghino Brevo SMTP',
                    message='Este es un mensaje de prueba para confirmar que Brevo SMTP está funcionando correctamente.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[destinatario],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"[OK] Correo de prueba enviado con éxito a {destinatario}."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[ERROR AL ENVIAR] {e}"))
                diag = diagnosticar_error_smtp(str(e))
                if diag:
                    self.stdout.write(self.style.NOTICE(f"-> {diag}"))
        else:
            self.stdout.write(self.style.SUCCESS(
                "\nPara enviar un correo de prueba real, ejecutá:\n"
                "python manage.py probar_brevo tu_correo@ejemplo.com"
            ))
