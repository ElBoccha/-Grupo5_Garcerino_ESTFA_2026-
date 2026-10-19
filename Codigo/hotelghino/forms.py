from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Usuario, Alojamiento, Habitacion, SolicitudPropietario, Reserva, ServicioAlojamiento

# Límite de tamaño para archivos de imagen (10 MB)
IMAGEN_MAX_BYTES = 10 * 1024 * 1024

# Firmas mágicas (magic bytes) de formatos de imagen permitidos
MAGIC_BYTES_IMAGENES = [
    (b'\xff\xd8\xff', 'JPEG'),
    (b'\x89PNG\r\n\x1a\n', 'PNG'),
    (b'GIF87a', 'GIF'),
    (b'GIF89a', 'GIF'),
    (b'BM', 'BMP'),
    (b'\x00\x00\x01\x00', 'ICO'),
]


def _es_webp(header_bytes):
    """Verifica firma WEBP: RIFF????WEBP"""
    return (len(header_bytes) >= 12
            and header_bytes[:4] == b'RIFF'
            and header_bytes[8:12] == b'WEBP')


def validar_archivo_imagen(archivo):
    """
    Valida que un archivo sea una imagen real verificando magic bytes.
    Rechaza PDFs, ejecutables y otros archivos no-imagen.
    Limita el tamaño a IMAGEN_MAX_BYTES.
    Deja el puntero del archivo en 0 al terminar.
    """
    if hasattr(archivo, 'size') and archivo.size > IMAGEN_MAX_BYTES:
        raise ValidationError(
            f'El archivo "{archivo.name}" es demasiado grande. '
            f'El tamaño máximo permitido es 10 MB.'
        )

    # Leer los primeros 12 bytes para verificar firma
    try:
        archivo.seek(0)
        header = archivo.read(12)
        archivo.seek(0)
    except Exception:
        raise ValidationError(f'No se pudo leer el archivo "{getattr(archivo, "name", "")}".')

    # Verificar firmas conocidas
    for magic, fmt in MAGIC_BYTES_IMAGENES:
        if header[:len(magic)] == magic:
            return  # Firma de imagen reconocida, OK

    if _es_webp(header):
        return  # WEBP, OK

    # Detectar PDF explícitamente para dar un mensaje claro
    if header[:4] == b'%PDF':
        raise ValidationError(
            f'El archivo "{getattr(archivo, "name", "")}" es un PDF. '
            'Solo se aceptan imágenes (JPG, PNG, WEBP, GIF).'
        )

    raise ValidationError(
        f'El archivo "{getattr(archivo, "name", "")}" no es una imagen válida. '
        'Se aceptan únicamente imágenes JPG, PNG, WEBP o GIF.'
    )


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        super().__init__(attrs)
        # Forzar el atributo en el widget por si Django no lo propaga
        self.attrs.setdefault('multiple', True)


class MultipleFileField(forms.FileField):
    """Campo que acepta múltiples archivos y valida cada uno individualmente."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            archivos = [single_clean(f, initial) for f in data]
        else:
            archivos = [single_clean(data, initial)] if data else []

        # Validar cada archivo con magic bytes
        for archivo in archivos:
            if archivo:
                validar_archivo_imagen(archivo)

        return archivos


class RegistroUsuario(UserCreationForm):
    """
    Formulario de registro inicial para nuevos usuarios del sistema.
    """
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'ejemplo@correo.com'})
    )

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

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('El correo electrónico es obligatorio.')
        if Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ya existe una cuenta registrada con este correo electrónico.')
        return email


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

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('El correo electrónico es obligatorio.')
        if self.instance and self.instance.pk:
            if Usuario.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Ya existe otra cuenta registrada con este correo electrónico.')
        return email

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
    ubicacion = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    latitud = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(),
    )
    longitud = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=6,
        widget=forms.HiddenInput(),
    )
    direccion_completa = forms.CharField(
        required=False,
        label='Dirección seleccionada',
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscá una dirección en el mapa o escribila aquí',
            'id': 'id_direccion_completa',
        }),
        help_text='Podés buscar en el mapa interactivo o escribir la dirección directamente.',
    )
    ciudad = forms.CharField(
        required=False,
        label='Ciudad o localidad',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: San Carlos de Bariloche',
            'id': 'id_ciudad',
        }),
    )
    provincia = forms.CharField(
        required=False,
        label='Provincia o región',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: Río Negro',
            'id': 'id_provincia',
        }),
    )
    pais = forms.CharField(
        required=False,
        initial='Argentina',
        widget=forms.HiddenInput(),
    )
    calle = forms.CharField(
        required=False,
        label='Calle',
        widget=forms.TextInput(attrs={
            "placeholder": "Ej: Av. San Martín",
            "id": "id_calle",
        }),
    )
    numero_calle = forms.CharField(
        required=False,
        label='Número',
        widget=forms.TextInput(attrs={
            "placeholder": "Ej: 450",
            "id": "id_numero_calle",
        }),
    )
    imagen_principal = forms.ImageField(
        required=False,
        label='Imagen principal (portada)',
        help_text='Imagen de portada del hotel. Formatos: JPG, PNG, WEBP.',
    )
    imagenes_extra = MultipleFileField(
        required=False,
        label='Imágenes adicionales (hasta 10)',
        help_text='Podés subir hasta 10 fotos más del hotel.',
    )

    class Meta:
        model = Alojamiento
        fields = [
            "nombre",
            "direccion_completa",
            "ciudad",
            "provincia",
            "pais",
            "latitud",
            "longitud",
            "calle",
            "numero_calle",
            "ubicacion",
            "descripcion",
            "servicios",
        ]
        labels = {
            "nombre": "Nombre del hotel",
            "direccion_completa": "Dirección completa",
            "ciudad": "Ciudad / Localidad",
            "provincia": "Provincia / Región",
            "calle": "Calle",
            "numero_calle": "Número",
            "descripcion": "Descripción",
        }
        widgets = {
            "calle": forms.TextInput(attrs={
                "placeholder": "Ej: Av. San Martín",
                "id": "id_calle",
            }),
            "numero_calle": forms.TextInput(attrs={
                "placeholder": "Ej: 1234",
                "id": "id_numero_calle",
            }),
            "descripcion": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Servicios, ubicación, comodidades principales...",
            }),
        }

    def clean_latitud(self):
        lat = self.cleaned_data.get('latitud')
        if lat is not None and (lat < -90 or lat > 90):
            raise forms.ValidationError('La latitud debe ser un valor válido entre -90 y 90.')
        return lat

    def clean_longitud(self):
        lng = self.cleaned_data.get('longitud')
        if lng is not None and (lng < -180 or lng > 180):
            raise forms.ValidationError('La longitud debe ser un valor válido entre -180 y 180.')
        return lng

    def clean_imagen_principal(self):
        imagen = self.cleaned_data.get('imagen_principal')
        if imagen:
            validar_archivo_imagen(imagen)
        return imagen

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitud')
        lng = cleaned_data.get('longitud')
        dir_comp = cleaned_data.get('direccion_completa', '').strip()
        ciudad = cleaned_data.get('ciudad', '').strip()
        calle = cleaned_data.get('calle', '').strip()
        num_calle = cleaned_data.get('numero_calle', '').strip()

        # Coherencia de coordenadas: deben estar ambas o ninguna
        if (lat is not None and lng is None) or (lat is None and lng is not None):
            self.add_error('latitud', 'Debés indicar tanto latitud como longitud.')

        # Si no se completó direccion_completa pero sí calle y número, componerla
        if not dir_comp and calle:
            partes = [f"{calle} {num_calle}".strip()]
            if ciudad:
                partes.append(ciudad)
            cleaned_data['direccion_completa'] = ", ".join(partes)

        # Sincronizar ciudad / ubicacion
        if ciudad and not cleaned_data.get('ubicacion'):
            cleaned_data['ubicacion'] = ciudad[:100]

        # Para nuevos alojamientos, exigir al menos una ubicación identificable
        if not self.instance.pk:
            if not dir_comp and not calle and not ciudad and lat is None:
                self.add_error('direccion_completa', 'Debés indicar la ubicación del hotel en el mapa o ingresar su dirección.')

        return cleaned_data


class HabitacionLoteForm(forms.Form):
    """
    Formulario para crear múltiples habitaciones de una vez, indicando un rango
    de números (ej: del 1 al 100). Todas comparten piso, tipo, capacidad y precio.
    """
    TIPOS_HABITACION = (
        ('Individual', 'Individual (1 persona)'),
        ('Doble', 'Doble (2 personas)'),
        ('Twin', 'Twin (2 camas individuales)'),
        ('Triple', 'Triple (3 personas)'),
        ('Cuadruple', 'Cuádruple (4 personas)'),
        ('Familiar', 'Familiar (hasta 6 personas)'),
        ('Suite', 'Suite'),
        ('Dormitorio compartido', 'Dormitorio compartido (hostel)'),
        ('Simple', 'Simple'),
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
    camas = forms.CharField(
        label='Camas (opcional)',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 1 cama matrimonial o 2 individuales'}),
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
        ('Individual', 'Individual (1 persona)'),
        ('Doble', 'Doble (2 personas)'),
        ('Twin', 'Twin (2 camas individuales)'),
        ('Triple', 'Triple (3 personas)'),
        ('Cuadruple', 'Cuádruple (4 personas)'),
        ('Familiar', 'Familiar (hasta 6 personas)'),
        ('Suite', 'Suite'),
        ('Dormitorio compartido', 'Dormitorio compartido (hostel)'),
        ('Simple', 'Simple'),
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
            "camas",
            "precio_noche",
            "descripcion",
            "disponible",
            "fecha_desocupacion_automatica",
        ]
        labels = {
            "numero_habitacion": "Numero de habitacion",
            "numero_piso": "Numero de piso",
            "capacidad_maxima": "Capacidad maxima",
            "tipo": "Tipo de habitacion",
            "camas": "Cantidad y tipo de camas",
            "precio_noche": "Precio por noche",
            "descripcion": "Descripción (opcional)",
            "disponible": "Disponible para reservar",
            "fecha_desocupacion_automatica": "No disponible hasta (opcional)",
        }
        widgets = {
            "camas": forms.TextInput(attrs={"placeholder": "Ej: 1 cama matrimonial"}),
            "descripcion": forms.Textarea(attrs={"rows": 2, "placeholder": "Detalles adicionales, comodidades..."}),
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


from .utils import obtener_fecha_limite_reserva


class ReservaForm(forms.ModelForm):
    """
    Formulario de reserva de habitación.
    Verifica coherencia de fechas y capacidad de huéspedes.
    """
    fecha_inicio = forms.DateField(
        label='Fecha de ingreso',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_finalizacion = forms.DateField(
        label='Fecha de salida',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    cantidad_huespedes = forms.IntegerField(
        label='Cantidad de huéspedes',
        min_value=1,
        initial=1,
        required=False,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 20, 'id': 'id_cantidad_huespedes'})
    )

    class Meta:
        model = Reserva
        fields = ['id_habitacion', 'fecha_inicio', 'fecha_finalizacion', 'cantidad_huespedes']
        labels = {
            'id_habitacion': 'Habitacion',
            'cantidad_huespedes': 'Cantidad de huéspedes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.now().date()
        max_fecha = obtener_fecha_limite_reserva(hoy)
        self.fields['fecha_inicio'].widget.attrs.update({
            'min': hoy.strftime('%Y-%m-%d'),
            'max': max_fecha.strftime('%Y-%m-%d'),
        })
        self.fields['fecha_finalizacion'].widget.attrs.update({
            'min': hoy.strftime('%Y-%m-%d'),
            'max': max_fecha.strftime('%Y-%m-%d'),
        })

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_finalizacion = cleaned_data.get('fecha_finalizacion')
        habitacion = cleaned_data.get('id_habitacion')
        cantidad_huespedes = cleaned_data.get('cantidad_huespedes') or 1
        cleaned_data['cantidad_huespedes'] = cantidad_huespedes

        hoy = timezone.now().date()
        max_fecha = obtener_fecha_limite_reserva(hoy)

        if fecha_inicio:
            if fecha_inicio < hoy:
                self.add_error('fecha_inicio', 'La fecha de ingreso no puede ser anterior a hoy.')
            elif fecha_inicio > max_fecha:
                self.add_error('fecha_inicio', 'La fecha de ingreso no puede superar 1 año en adelante.')

        if fecha_finalizacion:
            if fecha_finalizacion < hoy:
                self.add_error('fecha_finalizacion', 'La fecha de salida no puede ser anterior a hoy.')
            elif fecha_finalizacion > max_fecha:
                self.add_error('fecha_finalizacion', 'La fecha de salida no puede superar 1 año en adelante.')

        if fecha_inicio and fecha_finalizacion:
            if fecha_inicio >= fecha_finalizacion:
                self.add_error('fecha_finalizacion', 'La fecha de salida debe ser posterior a la fecha de ingreso.')

        if habitacion and cantidad_huespedes:
            if cantidad_huespedes > habitacion.capacidad_maxima:
                self.add_error(
                    'cantidad_huespedes',
                    f'La cantidad de huéspedes ({cantidad_huespedes}) no puede superar la capacidad máxima de la habitación seleccionada ({habitacion.capacidad_maxima} personas).'
                )

        return cleaned_data

