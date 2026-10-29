import os
from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError

# Límite máximo de tamaño de archivo (10 MB)
IMAGEN_MAX_BYTES = 10 * 1024 * 1024

EXTENSIONES_PERMITIDAS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
FORMATOS_PIL_PERMITIDOS = {'JPEG', 'PNG', 'WEBP', 'GIF'}


def validar_archivo_imagen(archivo):
    """
    Valida rigurosamente que el archivo subido sea una imagen auténtica, legible y permitida.
    - Rechaza explícitamente PDFs, documentos ejecutables u otros archivos no admitidos.
    - Limita el tamaño a 10 MB.
    - Inspecciona el contenido real mediante verificación de encabezado y Pillow (Image.open + verify).
    - Restaura siempre la posición del puntero del archivo a 0.
    """
    nombre = getattr(archivo, 'name', '') or ''
    _, ext = os.path.splitext(nombre.lower())

    # 1. Comprobación rápida por nombre de archivo
    if ext == '.pdf':
        raise ValidationError(
            f'El archivo "{nombre}" es un documento PDF. Solo se aceptan imágenes válidas (JPG, PNG, WEBP o GIF).'
        )

    if ext and ext not in EXTENSIONES_PERMITIDAS:
        raise ValidationError(
            f'La extensión "{ext}" no está permitida para imágenes. Formatos admitidos: JPG, PNG, WEBP o GIF.'
        )

    # 2. Comprobación de tamaño máximo
    size = getattr(archivo, 'size', None)
    if size is not None and size > IMAGEN_MAX_BYTES:
        mb = round(size / (1024 * 1024), 1)
        raise ValidationError(
            f'El archivo "{nombre}" supera el tamaño máximo permitido de 10 MB ({mb} MB).'
        )

    # 3. Comprobación de contenido binario (Detección de encabezado PDF o lectura defectuosa)
    try:
        archivo.seek(0)
        header = archivo.read(16)
        archivo.seek(0)
    except Exception:
        raise ValidationError(f'No se pudo leer el archivo "{nombre}".')

    if header.startswith(b'%PDF'):
        raise ValidationError(
            f'El archivo "{nombre}" contiene un documento PDF. Solo se admiten imágenes JPG, PNG, WEBP o GIF.'
        )

    # 4. Verificación profunda del contenido con Pillow
    try:
        archivo.seek(0)
        with Image.open(archivo) as img:
            img.verify()
            formato = (img.format or '').upper()
            if formato not in FORMATOS_PIL_PERMITIDOS:
                raise ValidationError(
                    f'El formato de imagen "{formato}" no está permitido. Solo se aceptan JPG, PNG, WEBP o GIF.'
                )
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ValidationError(
            f'El archivo "{nombre}" no es una imagen válida o está dañado.'
        )
    finally:
        try:
            archivo.seek(0)
        except Exception:
            pass
