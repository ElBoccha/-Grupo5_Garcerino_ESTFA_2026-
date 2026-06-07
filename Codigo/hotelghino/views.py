from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroUsuario
from .forms import RegistroAlojamiento
from .forms import SolicitudPropietarioForm
from .models import SolicitudPropietario


def registro(request):
    if request.method == 'POST':
        form = RegistroUsuario(request.POST)

        if form.is_valid():
            form.save()
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
    return render(request, 'home.html')


@login_required
def registroAlojamiento(request):
    if request.user.rol not in ['P', 'A']:
        messages.warning(request, 'Primero tenes que solicitar ser propietario y esperar la aprobacion.')
        return redirect('propietario')

    if request.method == 'POST':
        form = RegistroAlojamiento(request.POST)

        if form.is_valid():
            alojamiento = form.save(commit=False)
            alojamiento.id_usuario = request.user
            alojamiento.save()
            messages.success(request, 'Alojamiento registrado correctamente.')
            return redirect('home')
    else:
        form = RegistroAlojamiento()

    return render(request, 'registro-hoteles.html', {'form': form})


@login_required
def solicitudPropietario(request):
    if request.user.rol in ['P', 'A']:
        messages.info(request, 'Tu usuario ya puede registrar alojamientos.')
        return redirect('alojamientos')

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
