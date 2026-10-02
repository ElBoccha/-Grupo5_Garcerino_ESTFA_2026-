

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

## Instalación y ejecución local (desde cero)

**Requisitos previos:** [Python 3.10+](https://www.python.org/downloads/) (marcar "Add Python to PATH" al instalar; incluye pip) y [Git](https://git-scm.com/downloads).

1. Clonar el repositorio y entrar a la carpeta del proyecto:
```bash
   git clone https://github.com/ElBoccha/-Grupo5_Garcerino_ESTFA_2026-.git
   cd -Grupo5_Garcerino_ESTFA_2026-/Codigo
```

2. Crear y activar un entorno virtual nuevo (no usar `Codigo/venv`, fue creado en Linux):
   - Windows (PowerShell): `python -m venv .venv` y luego `.\.venv\Scripts\Activate.ps1`
   - Linux/macOS: `python3 -m venv .venv` y luego `source .venv/bin/activate`

3. Actualizar pip e instalar las dependencias (el `requirements.txt` está en la raíz del repo, un nivel arriba de `Codigo`):
```bash
   python -m pip install --upgrade pip
   pip install -r ../requirements.txt
```
   Si `pip` no se reconoce, usar `python -m pip install -r ../requirements.txt`.

4. Crear la base de datos (SQLite) y levantar el servidor:
```bash
   python manage.py migrate
   python manage.py runserver
```

5. Abrir `http://127.0.0.1:8000/` en el navegador.

> Si PowerShell bloquea la activación del entorno, ejecutar una vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.