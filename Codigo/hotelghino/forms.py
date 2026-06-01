from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from .models import Alojamiento

class RegistroUsuario(UserCreationForm):

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'dni',
            'telefono',
            'password1',
            'password2'
        ]


class RegistroAlojamiento(forms.ModelForm):

    class Meta:
        model = Alojamiento
        fields = [
            "nombre",
            "tipo",
            "calle",
            "numero_calle",
            "descripcion",
            "id_usuario",
        ]
