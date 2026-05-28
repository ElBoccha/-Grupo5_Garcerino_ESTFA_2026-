from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

# Create your views here.
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


    
    

