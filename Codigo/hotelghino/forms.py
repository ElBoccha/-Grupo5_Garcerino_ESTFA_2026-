from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Usuario, Alojamiento, Habitacion, SolicitudPropietario, Reserva, ServicioAlojamiento


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


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
    Incluye selección de servicios e imagen de portada.
    """
    servicios = forms.ModelMultipleChoiceField(
        queryset=ServicioAlojamiento.objects.all().order_by('orden'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Servicios del hotel',
    )
    imagen_principal = forms.ImageField(
        required=False,
        label='Imagen principal (portada)',
        help_text='Imagen de portada del hotel. Formatos: JPG, PNG, WEBP.',
    )
    imagenes_extra = forms.FileField(
        required=False,
        label='Imágenes adicionales (hasta 10)',
        help_text='Podés subir hasta 10 fotos más del hotel.',
        widget=MultipleFileInput(attrs={'multiple': True}),
    )

    class Meta:
        model = Alojamiento
        fields = [
            "nombre",
            "calle",
            "numero_calle",
            "descripcion",
            "servicios",
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


class HabitacionLoteForm(forms.Form):
    """
    Formulario para crear múltiples habitaciones de una vez, indicando un rango
    de números (ej: del 1 al 100). Todas comparten piso, tipo, capacidad y precio.
    """
    TIPOS_HABITACION = (
        ('Simple', 'Simple'),
        ('Doble', 'Doble'),
        ('Triple', 'Triple'),
        ('Suite', 'Suite'),
        ('Familiar', 'Familiar'),
    )

    hab_desde = forms.IntegerField(
        label='Desde la habitación N°',
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': '1'}),
    )
    hab_hasta = forms.IntegerField(
        label='Hasta la habitación N°',
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': '10'}),
    )
    numero_piso = forms.IntegerField(
        label='Piso',
        min_value=0,
        initial=1,
    )
    tipo = forms.ChoiceField(choices=TIPOS_HABITACION, label='Tipo de habitación')
    capacidad_maxima = forms.IntegerField(
        label='Capacidad máxima (personas)',
        min_value=1,
    )
    precio_noche = forms.IntegerField(
        label='Precio por noche ($)',
        min_value=1,
    )

    def clean(self):
        cleaned_data = super().clean()
        desde = cleaned_data.get('hab_desde')
        hasta = cleaned_data.get('hab_hasta')
        if desde and hasta:
            if hasta < desde:
                self.add_error('hab_hasta', 'El número final debe ser mayor o igual al inicial.')
            elif (hasta - desde + 1) > 200:
                self.add_error('hab_hasta', 'No podés crear más de 200 habitaciones a la vez.')
        return cleaned_data


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
    disponible = forms.BooleanField(
        label='Disponible para reservar',
        required=False,
        initial=True,
        help_text='Destildá esta opcion para marcar la habitacion como no disponible.'
    )
    fecha_desocupacion_automatica = forms.DateField(
        label='No disponible hasta (opcional)',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Si no está disponible, podés indicar hasta qué fecha para desocuparla automáticamente.'
    )

    class Meta:
        model = Habitacion
        fields = [
            "numero_habitacion",
            "numero_piso",
            "capacidad_maxima",
            "tipo",
            "precio_noche",
            "disponible",
            "fecha_desocupacion_automatica",
        ]
        labels = {
            "numero_habitacion": "Numero de habitacion",
            "numero_piso": "Numero de piso",
            "capacidad_maxima": "Capacidad maxima",
            "tipo": "Tipo de habitacion",
            "precio_noche": "Precio por noche",
            "disponible": "Disponible para reservar",
            "fecha_desocupacion_automatica": "No disponible hasta (opcional)",
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
