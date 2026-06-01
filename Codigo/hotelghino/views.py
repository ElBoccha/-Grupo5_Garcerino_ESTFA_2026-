from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import RegistroUsuario
from .forms import RegistroAlojamiento

# Create your views here.

# Formulario de registro

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuario(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')  

    else:
        form = RegistroUsuario()

    return render(request, 'registro.html', {'form': form})

# Vista de login

def login_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            return render(request, 'login.html', {"error": "Usuario o contraseña incorrectos"})
            
    

    return render(request, 'login.html')
    

# Vista principal

@login_required
def home(request):
    return render(request, 'home.html')

# Formulario de registro de alojamiento

def registroAlojamiento(request):
    if request.method == 'POST':
        form = RegistroAlojamiento(request.POST)

        if form.is_valid():
            form.save()

    else:
        form = RegistroAlojamiento()

    return render(request, 'registro-hoteles.html', {'form': form})


    
    

