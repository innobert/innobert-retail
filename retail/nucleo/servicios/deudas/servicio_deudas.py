"""Servicio para operaciones de deudas.

Hereda los métodos compartidos de BaseTransaccionServicio.
"""

from __future__ import annotations

import logging

from retail.nucleo.servicios.base.transaccion_base import BaseTransaccionServicio

logger = logging.getLogger(__name__)


class DeudasServicio(BaseTransaccionServicio):
    """Servicio para operaciones de deudas."""
