@echo off
setlocal

cd /d "%~dp0"

set "PORT=8020"
if not "%~1"=="" set "PORT=%~1"

set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

echo Proyecto actual: %CD%
echo Verificando Django...
"%PYTHON_EXE%" manage.py check
if errorlevel 1 (
    echo No se pudo verificar el proyecto. Revisar que las dependencias esten instaladas.
    pause
    exit /b 1
)

echo.
echo Servidor nuevo: http://127.0.0.1:%PORT%/
echo Si 8000 muestra una pagina vieja, usa este puerto o cerra el servidor anterior.
echo.
"%PYTHON_EXE%" manage.py runserver 127.0.0.1:%PORT% --noreload
