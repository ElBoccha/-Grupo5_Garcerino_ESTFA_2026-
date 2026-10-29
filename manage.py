#!/usr/bin/env python
"""
HotelGhino — manage.py Wrapper (Redirección automática a Codigo/)
Cuando se ejecuta desde la raíz del repositorio, este script redirige
transparentemente la ejecución a la carpeta 'Codigo' usando el entorno
virtual correcto de HotelGhino (.venv).
"""
import os
import sys
import subprocess


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    codigo_dir = os.path.join(root_dir, 'Codigo')
    target_manage = os.path.join(codigo_dir, 'manage.py')

    if not os.path.exists(target_manage):
        print(f"Error: No se encontró el proyecto en {codigo_dir}")
        sys.exit(1)

    # Detectar el Python del entorno virtual en Codigo
    venv_py_candidates = [
        os.path.join(codigo_dir, '.venv', 'Scripts', 'python.exe'),
        os.path.join(codigo_dir, 'venv', 'Scripts', 'python.exe'),
        sys.executable,
    ]
    python_exe = next((p for p in venv_py_candidates if os.path.exists(p)), sys.executable)

    args = sys.argv[1:]
    command_str = " ".join(args) if args else "help"
    print(f"\n[HotelGhino] -> Redirigiendo 'manage.py {command_str}' a: {codigo_dir}")
    print(f"[HotelGhino] -> Usando Python: {python_exe}\n")

    cmd = [python_exe, target_manage] + args
    try:
        proc = subprocess.run(cmd, cwd=codigo_dir)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
