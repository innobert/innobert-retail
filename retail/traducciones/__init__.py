"""
Módulo de internacionalización (i18n).

Uso:
    from retail.traducciones import _, establecer_idioma

    _("Hola mundo")   # → "Hello world" si el idioma es en
    _("Error: {0}").format(err)  # → "Error: {0}"
"""

import json
import os
from typing import Dict, Optional

_TRADUCCIONES: Dict[str, str] = {}
_IDIOMA_ACTUAL = "es"
_DIR = os.path.dirname(os.path.abspath(__file__))


def _cargar_idioma(idioma: str) -> Dict[str, str]:
    ruta = os.path.join(_DIR, f"{idioma}.json")
    if not os.path.exists(ruta):
        return {}
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def establecer_idioma(idioma: str) -> None:
    global _TRADUCCIONES, _IDIOMA_ACTUAL
    _IDIOMA_ACTUAL = idioma
    _TRADUCCIONES = _cargar_idioma(idioma)


def _(texto: str) -> str:
    return _TRADUCCIONES.get(texto, texto)


def idioma_actual() -> str:
    return _IDIOMA_ACTUAL


def _t(dominio: str, texto: str) -> str:
    """Traducción con prefijo de dominio para organización (opcional)."""
    clave = f"{dominio}.{texto}"
    return _TRADUCCIONES.get(clave, texto)


# Cargar español por defecto
establecer_idioma("es")
