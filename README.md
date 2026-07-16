

# -Grupo5_Garcerino_ESTFA_2026-
Este repositorio esta totalmente enfocado al desarrollo del proyecto Garcerino del grupo 5.

**Descripcion del proyecto:** Este proyecto consta de un gestionador de reservas turisticas. Para la realizacion de este proyecto debemos tener en cuenta la problematica principal brindada, donde se nos especifica que estos sistemas de reservas suelen ser manuales y poco eficientes, nuestra labor debe ser optimizar este sistema virtualmente.

**Lenguajes que utilizaremos:**

Base de datos: SQLite

Backend: Python.

Frontend: HTML y CSS.

**Roles de los integrantes:**

Garcia Federico: UX

Salierno Eduardo: DEV  

Gardino Lucas: DBA

Rende Manuel: DEV

Arce Federico: PM

**Color de Grupo:** Azul.

## Ejecucion local

El proyecto Django esta dentro de la carpeta `Codigo`.

1. Entrar a la carpeta:
   ```powershell
   cd Codigo
   ```
2. Instalar dependencias en un entorno virtual nuevo:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Aplicar migraciones y correr la pagina:
   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

La pagina queda disponible en `http://127.0.0.1:8000/`.

Nota: no uses la carpeta `Codigo/venv` que quedo en el repositorio, porque fue creada en Linux y no funciona bien en Windows. Crea un entorno nuevo con los pasos de arriba.

## Deploy en Render

El repositorio incluye `render.yaml` para crear el servicio desde Render Blueprint.

Si lo configuras manualmente en Render:

- Root Directory: `Codigo`
- Build Command: `bash build.sh`
- Start Command: `gunicorn fierro.wsgi:application --log-file -`
- Variables: `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS=.onrender.com`, `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`

Si usas una URL propia de Render o un dominio personalizado, agrega ese host a `ALLOWED_HOSTS` y su origen HTTPS a `CSRF_TRUSTED_ORIGINS`.
