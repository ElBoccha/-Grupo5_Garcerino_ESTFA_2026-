from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Usuario, Alojamiento, Habitacion, SolicitudPropietario, Reserva


class RegistroUsuario(UserCreationForm):
    """
    Formulario de registro inicial para nuevos usuarios del sistema.
    """
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
    """
    Formulario para editar el perfil del usuario activo, permitiendo
    actualizar datos personales y opcionalmente la contraseña.
    """
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
    """
    Formulario para el registro de nuevos alojamientos turísticos.
    """
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
    """
    Formulario para dar de alta o modificar habitaciones asociadas a un alojamiento.
    Valida que los valores numéricos sean positivos y mayores a cero donde corresponda.
    """
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
    """
    Formulario para que un huésped solicite el rol de propietario con un motivo explicativo.
    """
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


class ReservaForm(forms.ModelForm):
    """
    Formulario de reserva de habitación.
    Verifica coherencia de fechas: ingreso no anterior a hoy y salida posterior a ingreso.
    """
    fecha_inicio = forms.DateField(
        label='Fecha de ingreso',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_finalizacion = forms.DateField(
        label='Fecha de salida',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Reserva
        fields = ['id_habitacion', 'fecha_inicio', 'fecha_finalizacion']
        labels = {
            'id_habitacion': 'Habitacion',
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_finalizacion = cleaned_data.get('fecha_finalizacion')

        if fecha_inicio and fecha_finalizacion:
            if fecha_inicio >= fecha_finalizacion:
                self.add_error('fecha_finalizacion', 'La fecha de salida debe ser posterior a la fecha de ingreso.')

            if fecha_inicio < timezone.now().date():
                self.add_error('fecha_inicio', 'La fecha de ingreso no puede ser anterior a hoy.')

        return cleaned_data
