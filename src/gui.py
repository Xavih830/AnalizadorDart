# -*- coding: utf-8 -*-
"""
Redirección de compatibilidad para ejecutar la GUI como módulo individual.
"""

import sys
import os

# Ajuste de path para importación
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from gui import main

if __name__ == "__main__":
    main()
