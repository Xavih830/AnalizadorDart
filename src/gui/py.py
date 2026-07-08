# -*- coding: utf-8 -*-
"""
Shim de compatibilidad para ejecutar la GUI cuando se invoca erróneamente como 'python -m gui.py'.
Redirecciona la ejecución a src.gui.main().
"""

import sys
import os

# Ajuste dinámico de sys.path para permitir la ejecución autónoma desde dentro de la carpeta 'src/'
# o desde el directorio raíz del proyecto
_current_dir = os.path.dirname(os.path.abspath(__file__)) # src/gui
_src_dir = os.path.dirname(_current_dir) # src
_project_root = os.path.dirname(_src_dir) # root
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.gui import main

if __name__ == "__main__":
    main()
