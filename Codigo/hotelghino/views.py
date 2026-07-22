from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroUsuario
from .forms import ModificarUsuarioForm
from .forms import RegistroAlojamiento
from .forms import HabitacionForm
from .forms import SolicitudPropietarioForm
from .models import Alojamiento
from .models import Habitacion
from .models import SolicitudPropietario


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

    alojamientos = Alojamiento.objects.filter(estado='A').prefetch_related(
        'habitacion_set'
    ).order_by('-fecha_creacion')

    if destino:
        alojamientos = alojamientos.filter(
            Q(nombre__icontains=destino) |
            Q(calle__icontains=destino) |
            Q(descripcion__icontains=destino)
        )

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
