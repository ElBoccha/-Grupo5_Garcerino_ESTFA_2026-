from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Usuario
from .models import Alojamiento
from .models import Habitacion
from .models import SolicitudPropietario

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
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',
            'dni': 'DNI',
            'telefono': 'Telefono',
        }


class ModificarUsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Nueva contrasena',
        required=False,
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Confirmar nueva contrasena',
        required=False,
        widget=forms.PasswordInput
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'dni',
            'telefono',
        ]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'Las contrasenas no coinciden.')
            elif password1:
                try:
                    validate_password(password1, self.instance)
                except ValidationError as error:
                    self.add_error('password1', error)

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get('password1')

        if password:
            usuario.set_password(password)

        if commit:
            usuario.save()

        return usuario


class RegistroAlojamiento(forms.ModelForm):

    class Meta:
        model = Alojamiento
        fields = [
            "nombre",
            "calle",
            "numero_calle",
            "descripcion",
        ]
        labels = {
            "nombre": "Nombre del hotel",
            "calle": "Calle",
            "numero_calle": "Numero",
            "descripcion": "Descripcion",
        }
        widgets = {
            "descripcion": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Servicios, ubicacion, comodidades principales...",
            }),
        }


class HabitacionForm(forms.ModelForm):
    TIPOS_HABITACION = (
        ('Simple', 'Simple'),
        ('Doble', 'Doble'),
        ('Triple', 'Triple'),
        ('Suite', 'Suite'),
        ('Familiar', 'Familiar'),
    )

    tipo = forms.ChoiceField(choices=TIPOS_HABITACION, label='Tipo de habitacion')

    class Meta:
        model = Habitacion
        fields = [
            "numero_habitacion",
            "numero_piso",
            "capacidad_maxima",
            "tipo",
            "precio_noche",
        ]
        labels = {
            "numero_habitacion": "Numero de habitacion",
            "numero_piso": "Numero de piso",
            "capacidad_maxima": "Capacidad maxima",
            "tipo": "Tipo de habitacion",
            "precio_noche": "Precio por noche",
        }

    def clean(self):
        cleaned_data = super().clean()
        for field in ['numero_habitacion', 'numero_piso', 'capacidad_maxima', 'precio_noche']:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                self.add_error(field, 'El valor no puede ser negativo.')

        if cleaned_data.get('capacidad_maxima') == 0:
            self.add_error('capacidad_maxima', 'La capacidad debe ser mayor a cero.')

        if cleaned_data.get('precio_noche') == 0:
            self.add_error('precio_noche', 'El precio debe ser mayor a cero.')

        return cleaned_data


class SolicitudPropietarioForm(forms.ModelForm):

    class Meta:
        model = SolicitudPropietario
        fields = [
            "motivo",
        ]
        labels = {
            "motivo": "Motivo de la solicitud",
        }
        widgets = {
            "motivo": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Conta que tipo de alojamiento queres registrar.",
            }),
        }
