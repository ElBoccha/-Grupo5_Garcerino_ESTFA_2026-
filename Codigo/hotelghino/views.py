from datetime import datetime, date
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .forms import RegistroUsuario
from .forms import ModificarUsuarioForm
from .forms import RegistroAlojamiento
from .forms import HabitacionForm
from .forms import SolicitudPropietarioForm
from .forms import ReservaForm
from .models import Alojamiento
from .models import Habitacion
from .models import SolicitudPropietario
from .models import Reserva


def registro(request):
    if request.method == 'POST':
        form = RegistroUsuario(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado correctamente. Ya podes iniciar sesion.')
            return redirect('login')
    else:
        form = RegistroUsuario()

    return render(request, 'registro.html', {'form': form})


def recuperar_contrasena(request):
    """
    Vista custom de recuperacion de contraseña.
    - Si hay SMTP configurado (EMAIL_HOST_USER definido), envia el correo real.
    - Si no hay SMTP (desarrollo local), renderiza el enlace de reset directamente en pantalla.
    """
    Usuario = get_user_model()
    reset_link = None
    error = None
    enviado = False

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            error = 'Por favor ingresá un correo electrónico.'
        else:
            usuarios = Usuario.objects.filter(email__iexact=email, is_active=True)
            if usuarios.exists():
                for usuario in usuarios:
                    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
                    token = default_token_generator.make_token(usuario)
                    protocol = 'https' if request.is_secure() else 'http'
                    domain = request.get_host()
                    reset_url = f"{protocol}://{domain}/recuperar-contrasena/restablecer/{uid}/{token}/"

                    smtp_configurado = (
                        settings.EMAIL_BACKEND
                        != 'django.core.mail.backends.console.EmailBackend'
                    )

                    if smtp_configurado:
                        # Enviar correo real via Resend (anymail backend)
                        try:
                            html_message = render_to_string('password_reset_email.html', {
                                'user': usuario,
                                'uid': uid,
                                'token': token,
                                'protocol': protocol,
                                'domain': domain,
                            })
                            send_mail(
                                subject='Restablecer tu contraseña - Hotelghino',
                                message=f'Para restablecer tu contraseña, visitá: {reset_url}',
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[email],
                                html_message=html_message,
                                fail_silently=False,
                            )
                            enviado = True
                        except Exception as e:
                            error = f'Error al enviar el correo: {e}. Revisá la configuración de Resend.'
                    else:
                        # Sin SMTP: mostrar el enlace en pantalla (modo desarrollo)
                        reset_link = reset_url
                        enviado = True
                    break  # solo procesar el primer usuario
            else:
                # Siempre mostrar exito aunque no exista el email (seguridad)
                enviado = True

    return render(request, 'password_reset.html', {
        'reset_link': reset_link,
        'error': error,
        'enviado': enviado,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(request, 'login.html', {"error": "Usuario o contrasena incorrectos"})

    return render(request, 'login.html')


@login_required
def home(request):
    destino = request.GET.get('destino', '').strip()
    desde = request.GET.get('desde', '').strip()
    hasta = request.GET.get('hasta', '').strip()

    alojamientos = Alojamiento.objects.filter(
        Q(estado='A') | Q(estado='P'),
        tipo='HT'
    ).prefetch_related('habitacion_set').order_by('-fecha_creacion')

    if destino:
        alojamientos = alojamientos.filter(
            Q(nombre__icontains=destino) |
            Q(calle__icontains=destino) |
            Q(descripcion__icontains=destino)
        )

    if desde and hasta:
        try:
            d_inicio = datetime.strptime(desde, '%Y-%m-%d').date()
            d_fin = datetime.strptime(hasta, '%Y-%m-%d').date()
            if d_inicio < d_fin:
                reservas_ocupadas = Reserva.objects.filter(
                    fecha_inicio__lt=d_fin,
                    fecha_finalizacion__gt=d_inicio
                ).exclude(estado='Cancelada').values_list('id_habitacion_id', flat=True)

                alojamientos = alojamientos.filter(
                    Q(habitacion__isnull=True) | ~Q(habitacion__id__in=reservas_ocupadas)
                ).distinct()
        except ValueError:
            pass

    return render(request, 'home.html', {
        'alojamientos': alojamientos,
        'destino': destino,
        'desde': desde,
        'hasta': hasta,
    })


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Sesion cerrada correctamente.')
        return redirect('login')

    return redirect('home')


@login_required
def configuracion(request):
    return render(request, 'configuracion.html')


@login_required
def modificarUsuario(request):
    if request.method == 'POST':
        form = ModificarUsuarioForm(request.POST, instance=request.user)

        if form.is_valid():
            usuario = form.save()

            if form.cleaned_data.get('password1'):
                update_session_auth_hash(request, usuario)

            messages.success(request, 'Tus datos se actualizaron correctamente.')
            return redirect('home')
    else:
        form = ModificarUsuarioForm(instance=request.user)

    return render(request, 'modificar-usuario.html', {'form': form})


@login_required
def registroAlojamiento(request):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Primero tenes que solicitar ser propietario y esperar la aprobacion.')
        return redirect('propietario')

    if request.method == 'POST':
        form = RegistroAlojamiento(request.POST)

        if form.is_valid():
            alojamiento = form.save(commit=False)
            alojamiento.tipo = 'HT'
            alojamiento.estado = 'A'
            alojamiento.id_usuario = request.user
            alojamiento.save()
            messages.success(request, 'Hotel registrado correctamente. Ya podes cargar sus habitaciones.')
            return redirect('mis_hoteles')
    else:
        form = RegistroAlojamiento()

    return render(request, 'registro-hoteles.html', {'form': form})


@login_required
def misHoteles(request):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Solo los propietarios pueden administrar hoteles.')
        return redirect('home')

    alojamientos = Alojamiento.objects.filter(
        id_usuario=request.user,
        tipo='HT'
    ).prefetch_related('habitacion_set').order_by('-fecha_creacion')

    return render(request, 'mis-hoteles.html', {'alojamientos': alojamientos})


@login_required
def modificarAlojamiento(request, alojamiento_id):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Solo los propietarios pueden administrar hoteles.')
        return redirect('home')

    alojamiento = get_object_or_404(
        Alojamiento,
        pk=alojamiento_id,
        id_usuario=request.user,
        tipo='HT'
    )

    if request.method == 'POST':
        form = RegistroAlojamiento(request.POST, instance=alojamiento)

        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.tipo = 'HT'
            hotel.id_usuario = request.user
            hotel.save()
            messages.success(request, 'Hotel modificado correctamente.')
            return redirect('mis_hoteles')
    else:
        form = RegistroAlojamiento(instance=alojamiento)

    return render(request, 'formulario-hotel.html', {
        'form': form,
        'titulo': 'Modificar hotel',
        'boton': 'Guardar cambios',
    })


@login_required
def eliminarAlojamiento(request, alojamiento_id):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Solo los propietarios pueden administrar hoteles.')
        return redirect('home')

    alojamiento = get_object_or_404(
        Alojamiento,
        pk=alojamiento_id,
        id_usuario=request.user,
        tipo='HT'
    )

    if request.method == 'POST':
        alojamiento.delete()
        messages.success(request, 'Hotel eliminado correctamente.')
        return redirect('mis_hoteles')

    return render(request, 'confirmar-eliminacion.html', {
        'titulo': 'Eliminar hotel',
        'objeto': alojamiento.nombre,
        'cancelar_url': 'mis_hoteles',
    })


@login_required
def registroHabitacion(request, alojamiento_id):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Solo los propietarios pueden administrar habitaciones.')
        return redirect('home')

    alojamiento = get_object_or_404(
        Alojamiento,
        pk=alojamiento_id,
        id_usuario=request.user,
        tipo='HT'
    )

    if request.method == 'POST':
        form = HabitacionForm(request.POST)

        if form.is_valid():
            habitacion = form.save(commit=False)
            habitacion.id_alohamiento = alojamiento
            habitacion.id_usuario = request.user
            habitacion.save()
            messages.success(request, 'Habitacion registrada correctamente.')
            return redirect('mis_hoteles')
    else:
        form = HabitacionForm()

    return render(request, 'formulario-habitacion.html', {
        'form': form,
        'alojamiento': alojamiento,
        'titulo': 'Agregar habitacion',
        'boton': 'Registrar habitacion',
    })


@login_required
def modificarHabitacion(request, habitacion_id):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Solo los propietarios pueden administrar habitaciones.')
        return redirect('home')

    habitacion = get_object_or_404(
        Habitacion,
        pk=habitacion_id,
        id_usuario=request.user,
        id_alohamiento__id_usuario=request.user,
        id_alohamiento__tipo='HT'
    )

    if request.method == 'POST':
        form = HabitacionForm(request.POST, instance=habitacion)

        if form.is_valid():
            form.save()
            messages.success(request, 'Habitacion modificada correctamente.')
            return redirect('mis_hoteles')
    else:
        form = HabitacionForm(instance=habitacion)

    return render(request, 'formulario-habitacion.html', {
        'form': form,
        'alojamiento': habitacion.id_alohamiento,
        'titulo': 'Modificar habitacion',
        'boton': 'Guardar cambios',
    })


@login_required
def eliminarHabitacion(request, habitacion_id):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Solo los propietarios pueden administrar habitaciones.')
        return redirect('home')

    habitacion = get_object_or_404(
        Habitacion,
        pk=habitacion_id,
        id_usuario=request.user,
        id_alohamiento__id_usuario=request.user,
        id_alohamiento__tipo='HT'
    )

    if request.method == 'POST':
        habitacion.delete()
        messages.success(request, 'Habitacion eliminada correctamente.')
        return redirect('mis_hoteles')

    return render(request, 'confirmar-eliminacion.html', {
        'titulo': 'Eliminar habitacion',
        'objeto': f'Habitacion {habitacion.numero_habitacion}',
        'cancelar_url': 'mis_hoteles',
    })


@login_required
def solicitudPropietario(request):
    if request.user.rol == 'P':
        messages.info(request, 'Tu usuario ya puede registrar alojamientos.')
        return redirect('mis_hoteles')

    if request.user.rol == 'A':
        messages.info(request, 'Tu usuario administrador no necesita solicitar rol propietario.')
        return redirect('home')

    solicitud_pendiente = SolicitudPropietario.objects.filter(
        usuario=request.user,
        estado='P'
    ).exists()

    if request.method == 'POST':
        form = SolicitudPropietarioForm(request.POST)

        if solicitud_pendiente:
            messages.warning(request, 'Ya tenes una solicitud pendiente de revision.')
            return redirect('propietario')

        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.save()
            messages.success(request, 'Solicitud enviada correctamente. Un administrador la revisara.')
            return redirect('home')
    else:
        form = SolicitudPropietarioForm()

    return render(request, 'propietario.html', {
        'form': form,
        'solicitud_pendiente': solicitud_pendiente,
    })


@login_required
def detalleHotel(request, alojamiento_id):
    alojamiento = get_object_or_404(Alojamiento, pk=alojamiento_id)
    habitaciones = Habitacion.objects.filter(id_alohamiento=alojamiento).order_by('numero_habitacion')

    desde = request.GET.get('desde', '').strip()
    hasta = request.GET.get('hasta', '').strip()

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        form.fields['id_habitacion'].queryset = habitaciones

        if form.is_valid():
            habitacion = form.cleaned_data['id_habitacion']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_finalizacion = form.cleaned_data['fecha_finalizacion']

            if habitacion.id_alohamiento != alojamiento:
                messages.error(request, 'La habitacion seleccionada no pertenece a este hotel.')
                return redirect('detalle_hotel', alojamiento_id=alojamiento.id)

            solapada = Reserva.objects.filter(
                id_habitacion=habitacion,
                fecha_inicio__lt=fecha_finalizacion,
                fecha_finalizacion__gt=fecha_inicio
            ).exclude(estado='Cancelada').exists()

            if solapada:
                messages.error(request, 'La habitacion seleccionada no esta disponible para las fechas ingresadas.')
            else:
                dias = (fecha_finalizacion - fecha_inicio).days
                pago = dias * habitacion.precio_noche

                Reserva.objects.create(
                    fecha_inicio=fecha_inicio,
                    fecha_finalizacion=fecha_finalizacion,
                    estado='Confirmada',
                    pago=pago,
                    id_alohamiento=alojamiento,
                    id_usuario=request.user,
                    id_habitacion=habitacion
                )
                messages.success(request, f'¡Reserva confirmada en {alojamiento.nombre} para la habitacion {habitacion.numero_habitacion}! Total abonado: ${pago}.')
                return redirect('mis_reservas')
    else:
        initial_data = {}
        if desde:
            try:
                initial_data['fecha_inicio'] = datetime.strptime(desde, '%Y-%m-%d').date()
            except ValueError:
                pass
        if hasta:
            try:
                initial_data['fecha_finalizacion'] = datetime.strptime(hasta, '%Y-%m-%d').date()
            except ValueError:
                pass

        form = ReservaForm(initial=initial_data)
        form.fields['id_habitacion'].queryset = habitaciones

    return render(request, 'detalle-hotel.html', {
        'alojamiento': alojamiento,
        'habitaciones': habitaciones,
        'form': form,
        'desde': desde,
        'hasta': hasta,
    })


@login_required
def misReservas(request):
    reservas = Reserva.objects.filter(
        id_usuario=request.user
    ).select_related('id_alohamiento', 'id_habitacion').order_by('-fecha_inicio')

    return render(request, 'mis-reservas.html', {'reservas': reservas})


@login_required
def cancelarReserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id, id_usuario=request.user)

    if request.method == 'POST':
        reserva.estado = 'Cancelada'
        reserva.save()
        messages.success(request, 'Reserva cancelada correctamente.')
        return redirect('mis_reservas')

    return render(request, 'confirmar-eliminacion.html', {
        'titulo': 'Cancelar reserva',
        'objeto': f'Reserva en {reserva.id_alohamiento.nombre} ({reserva.fecha_inicio} al {reserva.fecha_finalizacion})',
        'cancelar_url': 'mis_reservas',
    })

