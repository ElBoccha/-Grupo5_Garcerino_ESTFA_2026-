import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Usuario, Alojamiento, Habitacion, SolicitudPropietario, Reserva, ServicioAlojamiento

from .validators import validar_archivo_imagen, IMAGEN_MAX_BYTES


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


# Categorías habituales de habitaciones turísticas, sin capacidad incrustada en el nombre.
# Se excluye 'Individual' ya que se unifica con 'Simple'.
CATEGORIAS_HABITACION = (
    ('Simple', 'Simple'),
    ('Doble', 'Doble'),
    ('Twin', 'Twin (dos camas individuales)'),
    ('Matrimonial', 'Matrimonial'),
    ('Triple', 'Triple'),
    ('Cuadruple', 'Cuádruple'),
    ('Familiar', 'Familiar'),
    ('Suite junior', 'Suite junior'),
    ('Suite', 'Suite'),
    ('Estudio o monoambiente', 'Estudio o monoambiente'),
    ('Departamento o apartamento', 'Departamento o apartamento'),
    ('Dormitorio compartido', 'Dormitorio compartido'),
)

# Para formularios se utilizan las categorías vigentes más las históricas existentes en la BD (excepto Individual)
TIPOS_HABITACION = CATEGORIAS_HABITACION + tuple(
    opt for opt in Habitacion.TIPOS if opt[0] not in [c[0] for c in CATEGORIAS_HABITACION] and opt[0] != 'Individual'
)

# Opciones separadas para selección de camas en formularios
OPCIONES_CAMAS_MATRIMONIALES = (
    (0, '0 (sin camas matrimoniales)'),
    (1, '1 cama matrimonial'),
    (2, '2 camas matrimoniales'),
    (3, '3 camas matrimoniales'),
    (4, '4 camas matrimoniales'),
)

OPCIONES_CAMAS_INDIVIDUALES = (
    (0, '0 (sin camas individuales)'),
    (1, '1 cama individual'),
    (2, '2 camas individuales'),
    (3, '3 camas individuales'),
    (4, '4 camas individuales'),
    (5, '5 camas individuales'),
    (6, '6 camas individuales'),
    (7, '7 camas individuales'),
    (8, '8 camas individuales'),
)


def parsear_camas(texto):
    """
    Extrae la cantidad de camas individuales y matrimoniales desde un texto o configuración preexistente.
    Retorna tupla (ind, mat).
    """
    if not texto:
        return 0, 0
    texto_str = str(texto).lower()
    mat = 0
    ind = 0

    # Buscar cantidad de camas matrimoniales
    m_mat = re.search(r'(\d+)\s*(?:cama[s]?\s*)?matrimonial', texto_str)
    if m_mat:
        mat = int(m_mat.group(1))
    elif 'matrimonial' in texto_str:
        mat = 1

    # Buscar cantidad de camas individuales
    m_ind = re.search(r'(\d+)\s*(?:cama[s]?\s*)?individual', texto_str)
    if m_ind:
        ind = int(m_ind.group(1))
    elif 'individual' in texto_str:
        ind = 1

    return ind, mat


def formatear_camas(camas_individuales, camas_matrimoniales):
    """
    Genera el texto descriptivo de las camas combinando matrimoniales e individuales por separado.
    Ej: '1 cama matrimonial + 2 camas individuales'
    """
    try:
        ind = int(camas_individuales or 0)
    except (ValueError, TypeError):
        ind = 0
    try:
        mat = int(camas_matrimoniales or 0)
    except (ValueError, TypeError):
        mat = 0

    partes = []
    if mat > 0:
        partes.append(f"{mat} cama matrimonial" if mat == 1 else f"{mat} camas matrimoniales")
    if ind > 0:
        partes.append(f"{ind} cama individual" if ind == 1 else f"{ind} camas individuales")

    return " + ".join(partes)

MODOS_NUMERACION_LOTE = (
    ('serie', 'En serie correlativa (números consecutivos, ej: 101 al 105)'),
    ('personalizada', 'Números específicos / no en serie (ej: 1, 3, 7, 10)'),
)


def parsear_numeros_habitacion(texto):
    """
    Parsea una cadena con números de habitación separados por comas, espacios,
    puntos y comas, o guiones para rangos (ej: '1, 3, 7, 10' o '101-104, 108').
    Tolera términos habituales como 'hab', 'habitación', 'la', 'el', 'n°'.
    Devuelve una lista ordenada de enteros positivos únicos.
    Lanza ValueError con mensaje descriptivo si encuentra valores no válidos.
    """
    if not texto:
        return []

    palabras_ignoradas = {
        'hab', 'hab.', 'habitacion', 'habitación', 'habitaciones',
        'n°', 'no.', 'no', 'num', 'núm', 'n', 'la', 'el', 'las', 'los', 'y'
    }

    # Normalizar separadores habituales
    texto_limpio = texto.replace(';', ',').replace('\n', ',')
    partes = [p.strip() for p in texto_limpio.split(',') if p.strip()]
    numeros = set()

    for parte in partes:
        # Soporte para rangos como '5-8' o '101-105'
        if '-' in parte:
            sub = parte.split('-')
            if len(sub) == 2 and sub[0].strip().isdigit() and sub[1].strip().isdigit():
                desde = int(sub[0].strip())
                hasta = int(sub[1].strip())
                if desde <= hasta:
                    if hasta - desde + 1 > 100:
                        raise ValueError(f"El rango '{parte}' supera el límite máximo de 100 habitaciones.")
                    for n in range(desde, hasta + 1):
                        if n > 0:
                            numeros.add(n)
                        else:
                            raise ValueError(f"El número {n} debe ser mayor a cero.")
                    continue
                else:
                    raise ValueError(f"El rango '{parte}' es inválido (el inicio debe ser menor o igual al final).")
            else:
                raise ValueError(f"El rango '{parte}' no tiene un formato válido.")

        # Subpartes separadas por espacio dentro de cada segmento
        sub_tokens = parte.split()
        for tok in sub_tokens:
            tok_lower = tok.lower().strip()
            if tok_lower in palabras_ignoradas:
                continue
            if tok.isdigit():
                val = int(tok)
                if val > 0:
                    numeros.add(val)
                else:
                    raise ValueError(f"El número {val} debe ser mayor a cero.")
            else:
                raise ValueError(f"'{tok}' no es un número de habitación válido.")

    if not numeros:
        raise ValueError("No se encontraron números de habitación válidos. Ingresá números como: 1, 3, 7, 10.")

    return sorted(list(numeros))


class HabitacionLoteForm(forms.Form):
    """
    Formulario para dar de alta múltiples habitaciones en lote para un alojamiento.
    Permite dos formas de numeración:
      1) Serie correlativa (número inicial y cantidad consecutiva).
      2) Números específicos / no en serie (ej: 1, 3, 7, 10).
    Separa de forma estricta la categoría del hotel de la capacidad máxima de personas.
    """
    TIPOS_HABITACION = TIPOS_HABITACION
    MODOS_NUMERACION = MODOS_NUMERACION_LOTE

    modo_numeracion = forms.ChoiceField(
        choices=MODOS_NUMERACION,
        initial='serie',
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'modo-numeracion-radio'}),
        label='Modo de numeración',
        help_text='Elegí si preferís crear una serie consecutiva o ingresar números específicos discontinuos.',
    )
    numero_inicial = forms.IntegerField(
        label='Número inicial de habitación',
        min_value=1,
        initial=101,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 101', 'min': 1}),
        help_text='Primer número de habitación para la serie correlativa.',
    )
    cantidad = forms.IntegerField(
        label='Cantidad de habitaciones a crear',
        min_value=1,
        max_value=100,
        initial=5,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 5', 'min': 1, 'max': 100}),
        help_text='Cantidad de habitaciones independientes a crear (1 a 100).',
    )
    numeros_personalizados = forms.CharField(
        label='Números específicos de habitación',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 1, 3, 7, 10 ó 101, 103, 105-108'}),
        help_text='Ingresá los números separados por coma o espacio (ej: 1, 3, 7, 10). Podés combinar rangos con guión.',
    )
    numero_piso = forms.IntegerField(
        label='Piso',
        min_value=0,
        initial=1,
        widget=forms.NumberInput(attrs={'placeholder': '1', 'min': 0}),
    )
    tipo = forms.ChoiceField(
        choices=TIPOS_HABITACION,
        label='Tipo de habitación (categoría)',
    )
    capacidad_maxima = forms.IntegerField(
        label='Capacidad máxima de huéspedes (personas)',
        min_value=1,
        max_value=50,
        initial=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 2', 'min': 1, 'max': 50}),
        help_text='Capacidad de huéspedes por habitación (rango habitual de 1 a 8 personas).',
    )
    precio_noche = forms.IntegerField(
        label='Precio por noche ($)',
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 15000', 'min': 1}),
    )
    camas_matrimoniales = forms.TypedChoiceField(
        choices=OPCIONES_CAMAS_MATRIMONIALES,
        coerce=int,
        required=False,
        initial=0,
        label='Camas matrimoniales',
        help_text='Cantidad de camas matrimoniales.',
    )
    camas_individuales = forms.TypedChoiceField(
        choices=OPCIONES_CAMAS_INDIVIDUALES,
        coerce=int,
        required=False,
        initial=0,
        label='Camas individuales',
        help_text='Cantidad de camas individuales.',
    )
    camas = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    descripcion = forms.CharField(
        label='Descripción común (opcional)',
        required=False,
        widget=forms.HiddenInput(),
    )
    disponible = forms.BooleanField(
        label='Disponibles para reservar',
        required=False,
        initial=True,
    )

    # Campos de compatibilidad con código previo o tests (hab_desde / hab_hasta)
    hab_desde = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput())
    hab_hasta = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput())

    def __init__(self, *args, alojamiento=None, **kwargs):
        self.alojamiento = alojamiento
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        modo = cleaned_data.get('modo_numeracion') or 'serie'
        nums_pers = (cleaned_data.get('numeros_personalizados') or '').strip()

        # Si se completó el campo de números específicos pero el modo quedó en serie,
        # o si el modo fue seleccionado explícitamente como personalizada:
        num_ini = cleaned_data.get('numero_inicial')
        cant = cleaned_data.get('cantidad')

        if modo == 'personalizada' or (nums_pers and (num_ini is None or not str(num_ini).strip())):
            modo = 'personalizada'
            cleaned_data['modo_numeracion'] = 'personalizada'

        lista_numeros = []

        if modo == 'personalizada':
            if not nums_pers:
                self.add_error('numeros_personalizados', 'Debés indicar los números de habitación a crear (ej: 1, 3, 7, 10).')
            else:
                try:
                    lista_numeros = parsear_numeros_habitacion(nums_pers)
                except ValueError as err:
                    self.add_error('numeros_personalizados', str(err))

                if lista_numeros:
                    if len(lista_numeros) > 100:
                        self.add_error('numeros_personalizados', 'No podés crear más de 100 habitaciones a la vez en un solo lote.')
        else:
            # Modo serie correlativa
            # Compatibilidad con hab_desde y hab_hasta históricos
            desde = cleaned_data.get('hab_desde')
            hasta = cleaned_data.get('hab_hasta')
            if (num_ini is None or cant is None) and (desde is not None and hasta is not None):
                if hasta < desde:
                    self.add_error('hab_hasta', 'El número final debe ser mayor o igual al inicial.')
                    return cleaned_data
                num_ini = desde
                cant = hasta - desde + 1
                cleaned_data['numero_inicial'] = num_ini
                cleaned_data['cantidad'] = cant

            if num_ini is None:
                self.add_error('numero_inicial', 'Debés indicar el número inicial para la serie correlativa.')
            elif num_ini < 1:
                self.add_error('numero_inicial', 'El número inicial debe ser mayor a cero.')

            if cant is None:
                self.add_error('cantidad', 'Debés indicar la cantidad de habitaciones a crear.')
            elif cant < 1:
                self.add_error('cantidad', 'La cantidad de habitaciones debe ser mayor a cero.')
            elif cant > 100:
                self.add_error('cantidad', 'No podés crear más de 100 habitaciones a la vez en un solo lote.')

            if num_ini and cant and 1 <= cant <= 100:
                lista_numeros = list(range(num_ini, num_ini + cant))

        cleaned_data['lista_numeros'] = lista_numeros

        capacidad = cleaned_data.get('capacidad_maxima')
        if capacidad is not None and capacidad < 1:
            self.add_error('capacidad_maxima', 'La capacidad debe ser mayor a cero.')

        precio = cleaned_data.get('precio_noche')
        if precio is not None and precio < 1:
            self.add_error('precio_noche', 'El precio por noche debe ser mayor a cero.')

        # Manejo de camas (individuales y matrimoniales por separado)
        camas_mat = cleaned_data.get('camas_matrimoniales')
        camas_ind = cleaned_data.get('camas_individuales')
        camas_directo = (cleaned_data.get('camas') or '').strip()

        if camas_mat or camas_ind:
            cleaned_data['camas'] = formatear_camas(camas_ind, camas_mat)
        elif camas_directo:
            ind_p, mat_p = parsear_camas(camas_directo)
            if ind_p > 0 or mat_p > 0:
                cleaned_data['camas'] = formatear_camas(ind_p, mat_p)
            else:
                cleaned_data['camas'] = camas_directo
        else:
            cleaned_data['camas'] = ''

        # Verificar unicidad de números de habitación dentro del alojamiento
        if self.alojamiento and lista_numeros:
            existentes = list(
                Habitacion.objects.filter(
                    id_alohamiento=self.alojamiento,
                    numero_habitacion__in=lista_numeros
                ).values_list('numero_habitacion', flat=True)
            )
            if existentes:
                existentes_str = ", ".join(str(n) for n in sorted(existentes))
                campo_error = 'numeros_personalizados' if modo == 'personalizada' else 'numero_inicial'
                self.add_error(
                    campo_error,
                    f'Las siguientes habitaciones ya existen en {self.alojamiento.nombre}: {existentes_str}. '
                    'Modificá los números para no duplicar habitaciones.'
                )

        return cleaned_data


class HabitacionForm(forms.ModelForm):
    """
    Formulario para dar de alta o modificar habitaciones asociadas a un alojamiento.
    Valida que los valores numéricos sean positivos y mayores a cero donde corresponda.
    Separa de forma estricta la categoría (tipo) de la capacidad máxima de huéspedes.
    """
    TIPOS_HABITACION = TIPOS_HABITACION

    tipo = forms.ChoiceField(
        choices=TIPOS_HABITACION,
        label='Tipo de habitación (categoría)',
    )
    camas_matrimoniales = forms.TypedChoiceField(
        choices=OPCIONES_CAMAS_MATRIMONIALES,
        coerce=int,
        required=False,
        initial=0,
        label='Camas matrimoniales',
        help_text='Seleccioná la cantidad de camas matrimoniales.',
    )
    camas_individuales = forms.TypedChoiceField(
        choices=OPCIONES_CAMAS_INDIVIDUALES,
        coerce=int,
        required=False,
        initial=0,
        label='Camas individuales',
        help_text='Seleccioná la cantidad de camas individuales.',
    )
    camas = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    capacidad_maxima = forms.IntegerField(
        label='Capacidad máxima de huéspedes (personas)',
        min_value=1,
        max_value=50,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 50, 'placeholder': 'Ej: 2 (1 a 8 habitual)'}),
        help_text='Cantidad de huéspedes que admite la habitación.',
    )
    precio_noche = forms.IntegerField(
        label='Precio por noche ($)',
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 15000', 'min': 1}),
    )
    disponible = forms.BooleanField(
        label='Disponible para reservar',
        required=False,
        initial=True,
        help_text='Destildá esta opción para marcar la habitación como no disponible.',
    )
    fecha_desocupacion_automatica = forms.DateField(
        label='No disponible hasta (opcional)',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Si no está disponible, podés indicar hasta qué fecha para desocuparla automáticamente.',
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
            "disponible",
            "fecha_desocupacion_automatica",
        ]
        labels = {
            "numero_habitacion": "Número de habitación",
            "numero_piso": "Piso",
            "capacidad_maxima": "Capacidad máxima de huéspedes",
            "tipo": "Tipo de habitación",
            "camas": "Configuración de camas",
            "precio_noche": "Precio por noche ($)",
            "disponible": "Disponible para reservar",
            "fecha_desocupacion_automatica": "No disponible hasta (opcional)",
        }
        widgets = {
            "numero_habitacion": forms.NumberInput(attrs={"placeholder": "101", "min": 1}),
            "numero_piso": forms.NumberInput(attrs={"placeholder": "1", "min": 0}),
        }

    def __init__(self, *args, alojamiento=None, **kwargs):
        self.alojamiento = alojamiento
        super().__init__(*args, **kwargs)
        if not self.alojamiento and self.instance and self.instance.pk:
            self.alojamiento = getattr(self.instance, 'id_alohamiento', None)

        if self.instance and self.instance.pk and self.instance.camas:
            ind, mat = parsear_camas(self.instance.camas)
            self.initial.setdefault('camas_individuales', ind)
            self.initial.setdefault('camas_matrimoniales', mat)

    def clean(self):
        cleaned_data = super().clean()
        for field in ['numero_habitacion', 'numero_piso', 'capacidad_maxima', 'precio_noche']:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                self.add_error(field, 'El valor no puede ser negativo.')

        if cleaned_data.get('capacidad_maxima') == 0:
            self.add_error('capacidad_maxima', 'La capacidad debe ser mayor a cero (mínimo 1 persona).')

        if cleaned_data.get('precio_noche') == 0:
            self.add_error('precio_noche', 'El precio debe ser mayor a cero.')

        # Manejo de camas (individuales y matrimoniales por separado)
        camas_mat = cleaned_data.get('camas_matrimoniales')
        camas_ind = cleaned_data.get('camas_individuales')
        camas_directo = (cleaned_data.get('camas') or '').strip()

        if camas_mat or camas_ind:
            cleaned_data['camas'] = formatear_camas(camas_ind, camas_mat)
        elif camas_directo:
            ind_p, mat_p = parsear_camas(camas_directo)
            if ind_p > 0 or mat_p > 0:
                cleaned_data['camas'] = formatear_camas(ind_p, mat_p)
            else:
                cleaned_data['camas'] = camas_directo
        else:
            cleaned_data['camas'] = ''

        # Validar que la fecha de desocupación no sea en el pasado
        fecha_desocupacion = cleaned_data.get('fecha_desocupacion_automatica')
        if fecha_desocupacion is not None:
            hoy = timezone.now().date()
            if fecha_desocupacion < hoy:
                self.add_error(
                    'fecha_desocupacion_automatica',
                    'La fecha de desocupación no puede ser anterior a la fecha actual.'
                )

        # Si hay fecha de desocupación futura (o igual a hoy), forzar disponible=False
        if fecha_desocupacion is not None and not self.errors.get('fecha_desocupacion_automatica'):
            hoy = timezone.now().date()
            if fecha_desocupacion >= hoy:
                cleaned_data['disponible'] = False
        elif cleaned_data.get('disponible'):
            cleaned_data['fecha_desocupacion_automatica'] = None

        # Validar unicidad del número de habitación dentro del alojamiento
        num_hab = cleaned_data.get('numero_habitacion')
        aloj = self.alojamiento or getattr(self.instance, 'id_alohamiento', None)
        if aloj and num_hab:
            qs = Habitacion.objects.filter(id_alohamiento=aloj, numero_habitacion=num_hab)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('numero_habitacion', f'Ya existe la habitación N° {num_hab} en este alojamiento.')

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

