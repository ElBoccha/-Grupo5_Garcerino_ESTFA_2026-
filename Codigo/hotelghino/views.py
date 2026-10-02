import json
from datetime import datetime, date
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .forms import RegistroUsuario
from .forms import ModificarUsuarioForm
from .forms import RegistroAlojamiento
from .forms import HabitacionForm
from .forms import HabitacionLoteForm
from .forms import SolicitudPropietarioForm
from .forms import ReservaForm
from .models import Alojamiento
from .models import Habitacion
from .models import SolicitudPropietario
from .models import Reserva
from .models import ServicioAlojamiento
from .models import ImagenAlojamiento


def sincronizar_disponibilidad_habitaciones():
    """
    Desocupa automáticamente aquellas habitaciones cuya reserva activa ha finalizado
    (es decir, cuya fecha de finalización es menor o igual a la fecha de hoy).
    """
    hoy = timezone.now().date()
    Habitacion.objects.filter(
        disponible=False,
        fecha_desocupacion_automatica__isnull=False,
        fecha_desocupacion_automatica__lte=hoy
    ).update(disponible=True, fecha_desocupacion_automatica=None)


def registro(request):
    if request.user.is_authenticated:
        return redirect('home')

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
                        not in (
                            'django.core.mail.backends.console.EmailBackend',
                            'django.core.mail.backends.locmem.EmailBackend',
                        )
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
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')

        return render(request, 'login.html', {"error": "Usuario o contrasena incorrectos"})

    return render(request, 'login.html')


def home(request):
    destino = request.GET.get('destino', '').strip()
    desde = request.GET.get('desde', '').strip()
    hasta = request.GET.get('hasta', '').strip()

    # Obtener solo hoteles aprobados (activos) ordenados por fecha
    alojamientos = Alojamiento.objects.filter(
        estado='A',
        tipo='HT'
    ).prefetch_related('habitacion_set').order_by('-fecha_creacion')

    # Ciudades y destinos turísticos clasificados por región
    ciudades_turisticas = [
        # Costa Atlántica
        {"nombre": "Mar del Plata", "region": "Costa", "provincia": "Buenos Aires"},
        {"nombre": "Mar del Tuyú", "region": "Costa", "provincia": "Partido de La Costa"},
        {"nombre": "Pinamar", "region": "Costa", "provincia": "Buenos Aires"},
        {"nombre": "Villa Gesell", "region": "Costa", "provincia": "Buenos Aires"},
        {"nombre": "San Bernardo", "region": "Costa", "provincia": "Partido de La Costa"},
        {"nombre": "Santa Clara del Mar", "region": "Costa", "provincia": "Mar Chiquita"},
        {"nombre": "Cariló", "region": "Costa", "provincia": "Pinamar"},
        {"nombre": "San Clemente del Tuyú", "region": "Costa", "provincia": "Partido de La Costa"},
        {"nombre": "Mar de las Pampas", "region": "Costa", "provincia": "Villa Gesell"},
        {"nombre": "Miramar", "region": "Costa", "provincia": "Buenos Aires"},
        {"nombre": "Necochea", "region": "Costa", "provincia": "Buenos Aires"},
        {"nombre": "Monte Hermoso", "region": "Costa", "provincia": "Buenos Aires"},
        {"nombre": "Las Grutas", "region": "Costa", "provincia": "Río Negro"},
        # Patagonia y Lagos
        {"nombre": "Bariloche", "region": "Patagonia", "provincia": "Río Negro"},
        {"nombre": "San Martín de los Andes", "region": "Patagonia", "provincia": "Neuquén"},
        {"nombre": "Villa La Angostura", "region": "Patagonia", "provincia": "Neuquén"},
        {"nombre": "El Calafate", "region": "Patagonia", "provincia": "Santa Cruz"},
        {"nombre": "El Chaltén", "region": "Patagonia", "provincia": "Santa Cruz"},
        {"nombre": "Ushuaia", "region": "Patagonia", "provincia": "Tierra del Fuego"},
        {"nombre": "Puerto Madryn", "region": "Patagonia", "provincia": "Chubut"},
        # Sierras y Centro
        {"nombre": "Villa Carlos Paz", "region": "Sierras", "provincia": "Córdoba"},
        {"nombre": "Villa General Belgrano", "region": "Sierras", "provincia": "Córdoba"},
        {"nombre": "Merlo", "region": "Sierras", "provincia": "San Luis"},
        {"nombre": "Mina Clavero", "region": "Sierras", "provincia": "Córdoba"},
        {"nombre": "La Cumbrecita", "region": "Sierras", "provincia": "Córdoba"},
        {"nombre": "Tandil", "region": "Sierras", "provincia": "Buenos Aires"},
        {"nombre": "Sierra de la Ventana", "region": "Sierras", "provincia": "Buenos Aires"},
        {"nombre": "Capilla del Monte", "region": "Sierras", "provincia": "Córdoba"},
        # Cuyo, Norte y Litoral
        {"nombre": "Mendoza", "region": "Cuyo", "provincia": "Mendoza"},
        {"nombre": "San Rafael", "region": "Cuyo", "provincia": "Mendoza"},
        {"nombre": "Cafayate", "region": "Norte", "provincia": "Salta"},
        {"nombre": "Purmamarca", "region": "Norte", "provincia": "Jujuy"},
        {"nombre": "Tilcara", "region": "Norte", "provincia": "Jujuy"},
        {"nombre": "Puerto Iguazú", "region": "Litoral", "provincia": "Misiones"},
        {"nombre": "Colón", "region": "Litoral", "provincia": "Entre Ríos"},
        {"nombre": "Federación", "region": "Litoral", "provincia": "Entre Ríos"},
        {"nombre": "Gualeguaychú", "region": "Litoral", "provincia": "Entre Ríos"},
    ]

    # Obtener hoteles activos registrados para sugerir también por nombre de hotel
    hoteles_sugeridos = []
    for h in Alojamiento.objects.filter(estado='A', tipo='HT').values('id', 'nombre', 'calle', 'numero_calle'):
        nombre_clean = h['nombre'].strip()
        if len(nombre_clean) >= 3:
            ubicacion = f"{h['calle']} {h['numero_calle']}".strip()
            hoteles_sugeridos.append({
                'nombre': nombre_clean,
                'region': 'Hotel',
                'provincia': ubicacion or 'Hotel registrado',
                'es_hotel': True,
            })

    # Lista plana para compatibilidad con datalist / formularios
    destinos_sugeridos = [c['nombre'] for c in ciudades_turisticas]

    if destino:
        destino_lower = destino.lower()
        destino_norm = (
            destino_lower.replace('á', 'a')
            .replace('é', 'e')
            .replace('í', 'i')
            .replace('ó', 'o')
            .replace('ú', 'u')
        )
        filtro_destino = (
            Q(nombre__icontains=destino) |
            Q(calle__icontains=destino) |
            Q(descripcion__icontains=destino)
        )
        if destino_norm != destino_lower:
            filtro_destino |= (
                Q(nombre__icontains=destino_norm) |
                Q(calle__icontains=destino_norm) |
                Q(descripcion__icontains=destino_norm)
            )

        alojamientos = alojamientos.filter(filtro_destino)

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

    # Combinación para el autocompletado en JSON
    combo_sugerencias = ciudades_turisticas + hoteles_sugeridos

    return render(request, 'home.html', {
        'alojamientos': alojamientos,
        'destino': destino,
        'desde': desde,
        'hasta': hasta,
        'destinos_sugeridos': destinos_sugeridos,
        'combo_sugerencias_json': json.dumps(combo_sugerencias, ensure_ascii=False),
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

    # Asegurar que los servicios predefinidos existen en la base de datos
    if not ServicioAlojamiento.objects.exists():
        ServicioAlojamiento.poblar_servicios()

    if request.method == 'POST':
        form = RegistroAlojamiento(request.POST, request.FILES)
        lote_form = HabitacionLoteForm(request.POST)
        agregar_lote = request.POST.get('agregar_habitaciones') in ['1', 'true', 'on', 'True', True] or request.POST.get('crear_habitaciones_lote') in ['1', 'true', 'on', 'True', True]

        form_ok = form.is_valid()
        lote_ok = (not agregar_lote) or lote_form.is_valid()

        if form_ok and lote_ok:
            alojamiento = form.save(commit=False)
            alojamiento.tipo = 'HT'
            alojamiento.estado = 'P'
            alojamiento.id_usuario = request.user
            alojamiento.save()
            # Guardar la relación M2M de servicios
            form.save_m2m()

            # Imagen principal
            imagen_principal = request.FILES.get('imagen_principal')
            if imagen_principal:
                # Eliminar portada previa si existe
                ImagenAlojamiento.objects.filter(
                    alojamiento=alojamiento, es_principal=True
                ).delete()
                ImagenAlojamiento.objects.create(
                    alojamiento=alojamiento,
                    imagen=imagen_principal,
                    es_principal=True,
                    orden=0,
                )

            # Imágenes extra (múltiples archivos)
            imagenes_extra = request.FILES.getlist('imagenes_extra')
            imagenes_existentes = ImagenAlojamiento.objects.filter(
                alojamiento=alojamiento, es_principal=False
            ).count()
            permitidas = max(0, 10 - imagenes_existentes)
            for i, img in enumerate(imagenes_extra[:permitidas]):
                ImagenAlojamiento.objects.create(
                    alojamiento=alojamiento,
                    imagen=img,
                    es_principal=False,
                    orden=imagenes_existentes + i + 1,
                )
            if len(imagenes_extra) > permitidas:
                messages.warning(request, f'Solo se cargaron {permitidas} imágenes extra (límite: 10).')

            # Habitaciones en lote
            if agregar_lote and lote_ok:
                lote = lote_form.cleaned_data
                creadas = 0
                for num in range(lote['hab_desde'], lote['hab_hasta'] + 1):
                    if not Habitacion.objects.filter(
                        id_alohamiento=alojamiento,
                        numero_habitacion=num
                    ).exists():
                        Habitacion.objects.create(
                            numero_habitacion=num,
                            numero_piso=lote['numero_piso'],
                            capacidad_maxima=lote['capacidad_maxima'],
                            tipo=lote['tipo'],
                            precio_noche=lote['precio_noche'],
                            disponible=True,
                            id_alohamiento=alojamiento,
                            id_usuario=request.user,
                        )
                        creadas += 1
                messages.success(
                    request,
                    f'Hotel registrado. Se crearon {creadas} habitaciones (N° {lote["hab_desde"]} a {lote["hab_hasta"]}).'
                )
            else:
                messages.success(request, 'Hotel registrado correctamente. Queda en estado pendiente hasta la aprobación del administrador.')

            return redirect('mis_hoteles')
    else:
        form = RegistroAlojamiento()
        lote_form = HabitacionLoteForm()

    return render(request, 'registro-hoteles.html', {
        'form': form,
        'lote_form': lote_form,
        'servicios': ServicioAlojamiento.objects.all().order_by('orden'),
    })


@login_required
def misHoteles(request):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Solo los propietarios pueden administrar hoteles.')
        return redirect('home')

    sincronizar_disponibilidad_habitaciones()

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
        form = RegistroAlojamiento(request.POST, request.FILES, instance=alojamiento)

        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.tipo = 'HT'
            hotel.id_usuario = request.user
            hotel.save()
            form.save_m2m()

            # Imagen principal (si se carga una nueva, reemplaza la anterior)
            imagen_principal = request.FILES.get('imagen_principal')
            if imagen_principal:
                ImagenAlojamiento.objects.filter(
                    alojamiento=hotel, es_principal=True
                ).delete()
                ImagenAlojamiento.objects.create(
                    alojamiento=hotel,
                    imagen=imagen_principal,
                    es_principal=True,
                    orden=0,
                )

            # Imágenes extra
            imagenes_extra = request.FILES.getlist('imagenes_extra')
            imagenes_existentes = ImagenAlojamiento.objects.filter(
                alojamiento=hotel, es_principal=False
            ).count()
            permitidas = max(0, 10 - imagenes_existentes)
            for i, img in enumerate(imagenes_extra[:permitidas]):
                ImagenAlojamiento.objects.create(
                    alojamiento=hotel,
                    imagen=img,
                    es_principal=False,
                    orden=imagenes_existentes + i + 1,
                )
            if len(imagenes_extra) > permitidas:
                messages.warning(request, f'Solo se cargaron {permitidas} imágenes extra (límite: 10).')

            messages.success(request, 'Hotel modificado correctamente.')
            return redirect('mis_hoteles')
    else:
        form = RegistroAlojamiento(instance=alojamiento)

    return render(request, 'formulario-hotel.html', {
        'form': form,
        'titulo': 'Modificar hotel',
        'boton': 'Guardar cambios',
        'alojamiento': alojamiento,
        'servicios': ServicioAlojamiento.objects.all().order_by('orden'),
        'img_principal': alojamiento.imagenes.filter(es_principal=True).first(),
        'imgs_extra': alojamiento.imagenes.filter(es_principal=False),
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

    if alojamiento.estado == 'R':
        messages.warning(request, 'No podés agregar habitaciones a un hotel rechazado.')
        return redirect('mis_hoteles')

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
    sincronizar_disponibilidad_habitaciones()
    alojamiento = get_object_or_404(Alojamiento, pk=alojamiento_id)
    habitaciones = Habitacion.objects.filter(id_alohamiento=alojamiento).order_by('numero_habitacion')

    desde = request.GET.get('desde', '').strip() or request.POST.get('fecha_inicio', '').strip()
    hasta = request.GET.get('hasta', '').strip() or request.POST.get('fecha_finalizacion', '').strip()

    # Calcular disponibilidad de habitaciones para el rango de fechas dado
    fechas_validas = False
    d_inicio = None
    d_fin = None
    ids_ocupadas_por_reserva = set()

    if desde and hasta:
        try:
            d_inicio = datetime.strptime(desde, '%Y-%m-%d').date()
            d_fin = datetime.strptime(hasta, '%Y-%m-%d').date()
            if d_inicio < d_fin:
                fechas_validas = True
                # IDs de habitaciones con reservas solapadas (no canceladas)
                ids_ocupadas_por_reserva = set(
                    Reserva.objects.filter(
                        id_alohamiento=alojamiento,
                        fecha_inicio__lt=d_fin,
                        fecha_finalizacion__gt=d_inicio
                    ).exclude(estado='Cancelada').values_list('id_habitacion_id', flat=True)
                )
        except ValueError:
            pass

    # Anotar cada habitación con su estado para las fechas pedidas
    habitaciones_con_estado = []
    habitaciones_disponibles_ids = []
    for hab in habitaciones:
        if fechas_validas:
            # Ocupada si: el propietario la marcó manualmente como no disponible,
            # O si tiene una reserva solapada en esas fechas
            ocupada = (not hab.disponible) or (hab.id in ids_ocupadas_por_reserva)
        else:
            # Sin fechas: mostrar estado manual del propietario
            ocupada = not hab.disponible
        hab.esta_disponible = not ocupada
        habitaciones_con_estado.append(hab)
        if not ocupada:
            habitaciones_disponibles_ids.append(hab.id)

    habitaciones_disponibles_qs = habitaciones.filter(id__in=habitaciones_disponibles_ids)

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        form.fields['id_habitacion'].queryset = habitaciones_disponibles_qs

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

            if not habitacion.disponible:
                messages.error(request, 'La habitacion seleccionada no esta disponible para reservar.')
            elif solapada:
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
                # Marcar habitación como no disponible automáticamente y fijar desocupación al terminar
                habitacion.disponible = False
                habitacion.fecha_desocupacion_automatica = fecha_finalizacion
                habitacion.save(update_fields=['disponible', 'fecha_desocupacion_automatica'])

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
        form.fields['id_habitacion'].queryset = habitaciones_disponibles_qs

    return render(request, 'detalle-hotel.html', {
        'alojamiento': alojamiento,
        'habitaciones': habitaciones_con_estado,
        'habitaciones_disponibles': habitaciones_disponibles_qs,
        'form': form,
        'desde': desde,
        'hasta': hasta,
        'fechas_validas': fechas_validas,
        'd_inicio': d_inicio,
        'd_fin': d_fin,
        'img_principal': alojamiento.imagenes.filter(es_principal=True).first(),
        'imgs_galeria': alojamiento.imagenes.filter(es_principal=False).order_by('orden'),
        'servicios': alojamiento.servicios.all().order_by('orden'),
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

        # Liberar habitación automáticamente si no quedan reservas activas vigentes o futuras
        habitacion = reserva.id_habitacion
        hoy = timezone.now().date()
        proxima_reserva = Reserva.objects.filter(
            id_habitacion=habitacion,
            fecha_finalizacion__gt=hoy
        ).exclude(estado='Cancelada').exclude(pk=reserva.pk).order_by('fecha_finalizacion').last()

        if proxima_reserva:
            habitacion.fecha_desocupacion_automatica = proxima_reserva.fecha_finalizacion
            habitacion.save(update_fields=['fecha_desocupacion_automatica'])
        else:
            habitacion.disponible = True
            habitacion.fecha_desocupacion_automatica = None
            habitacion.save(update_fields=['disponible', 'fecha_desocupacion_automatica'])

        messages.success(request, 'Reserva cancelada correctamente.')
        return redirect('mis_reservas')

    return render(request, 'confirmar-eliminacion.html', {
        'titulo': 'Cancelar reserva',
        'objeto': f'Reserva en {reserva.id_alohamiento.nombre} ({reserva.fecha_inicio} al {reserva.fecha_finalizacion})',
        'cancelar_url': 'mis_reservas',
    })


@login_required
def toggleDisponibilidadHabitacion(request, habitacion_id):
    """
    Permite al propietario cambiar el estado de disponibilidad de una habitacion
    con un solo POST. Accesible solo para propietarios dueños de la habitacion.
    """
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
        habitacion.disponible = not habitacion.disponible
        habitacion.fecha_desocupacion_automatica = None
        habitacion.save(update_fields=['disponible', 'fecha_desocupacion_automatica'])
        estado = 'disponible' if habitacion.disponible else 'no disponible'
        messages.success(request, f'Habitacion {habitacion.numero_habitacion} marcada como {estado}.')
        return redirect('mis_hoteles')

    return redirect('mis_hoteles')


@login_required
def gestionarImagenesHotel(request, alojamiento_id):
    """
    Permite al propietario subir y eliminar imágenes de su hotel.
    - GET: muestra galería actual + formulario de subida.
    - POST action=subir: sube imagen principal y/o fotos extra.
    - POST action=eliminar: elimina una imagen por id.
    """
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Solo los propietarios pueden gestionar imágenes.')
        return redirect('home')

    alojamiento = get_object_or_404(
        Alojamiento,
        pk=alojamiento_id,
        id_usuario=request.user,
        tipo='HT'
    )

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'eliminar':
            imagen_id = request.POST.get('imagen_id')
            if imagen_id:
                ImagenAlojamiento.objects.filter(
                    pk=imagen_id,
                    alojamiento=alojamiento
                ).delete()
                messages.success(request, 'Imagen eliminada correctamente.')
            return redirect('gestionar_imagenes', alojamiento_id=alojamiento.id)

        if action == 'subir':
            # Imagen principal
            imagen_principal = request.FILES.get('imagen_principal')
            if imagen_principal:
                ImagenAlojamiento.objects.filter(
                    alojamiento=alojamiento, es_principal=True
                ).delete()
                ImagenAlojamiento.objects.create(
                    alojamiento=alojamiento,
                    imagen=imagen_principal,
                    es_principal=True,
                    orden=0,
                )
                messages.success(request, 'Imagen principal actualizada.')

            # Imágenes extra (múltiples)
            imagenes_extra = request.FILES.getlist('imagenes_extra')
            if imagenes_extra:
                existentes = ImagenAlojamiento.objects.filter(
                    alojamiento=alojamiento, es_principal=False
                ).count()
                permitidas = max(0, 10 - existentes)
                for i, img in enumerate(imagenes_extra[:permitidas]):
                    ImagenAlojamiento.objects.create(
                        alojamiento=alojamiento,
                        imagen=img,
                        es_principal=False,
                        orden=existentes + i + 1,
                    )
                if permitidas > 0:
                    messages.success(request, f'Se subieron {min(len(imagenes_extra), permitidas)} imágenes adicionales.')
                if len(imagenes_extra) > permitidas:
                    messages.warning(request, f'Límite alcanzado: solo se cargaron {permitidas} de {len(imagenes_extra)} fotos (máximo 10 extra).')

            return redirect('gestionar_imagenes', alojamiento_id=alojamiento.id)

    img_principal = alojamiento.imagenes.filter(es_principal=True).first()
    imgs_extra = alojamiento.imagenes.filter(es_principal=False).order_by('orden')

    return render(request, 'gestionar-imagenes.html', {
        'alojamiento': alojamiento,
        'img_principal': img_principal,
        'imgs_extra': imgs_extra,
        'total_extra': imgs_extra.count(),
    })
