from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')  # nombre de tu url login

    else:
        form = UserCreationForm()

    return render(request, 'registro.html', {'form': form})

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
    


@login_required
def home(request):
    return render(request, 'home.html')


    
    

