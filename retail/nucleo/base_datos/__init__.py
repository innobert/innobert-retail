"""
base_datos - Paquete refactorizado de gestión de base de datos SQLite.

Re-exporta todas las funciones del módulo monolítico original
para mantener compatibilidad con el código existente.
"""

from __future__ import annotations

import sys
import types
from typing import Any

# Re-exportar desde configuraciones para compatibilidad
from retail.nucleo.configuraciones import (
    asegurar_directorios,
    obtener_ruta_base_datos,
)

# ===================================================================
# DB_NAME como propiedad ligada a config_db (mutable para tests)
# ===================================================================

from retail.nucleo.base_datos._config_db import config_db

# Sincronizar con la ruta actual (importante tras importlib.reload en tests)
config_db.nombre = obtener_ruta_base_datos()

# ------------------------------------------------------------------
# conexion.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.conexion import (
    conexion,
    ejecutar_consulta,
    obtener_conexion,
)

# ------------------------------------------------------------------
# indices.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.indices import (
    IDX_PROD_COSTO,
    IDX_PROD_ESTADO,
    IDX_PROD_ID,
    IDX_PROD_IMAGEN,
    IDX_PROD_NOMBRE,
    IDX_PROD_PRECIO,
    IDX_PROD_STOCK,
    producto_a_dict,
)

# ------------------------------------------------------------------
# esquema.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.esquema import crear_tablas

# ------------------------------------------------------------------
# clientes.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.clientes import (
    actualizar_cliente,
    buscar_cliente_por_cedula,
    combobox_clientes,
    eliminar_cliente,
    insertar_cliente,
    obtener_clientes,
)

# ------------------------------------------------------------------
# inventario.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.inventario import (
    actualizar_producto,
    agregar_producto,
    buscar_productos_por_nombre,
    combobox_productos,
    contar_productos,
    editar_producto,
    eliminar_producto,
    obtener_nombres_productos,
    obtener_productos,
    obtener_totales_globales_ganancias,
    paginar_productos,
    registrar_historial_inventario,
)

# ------------------------------------------------------------------
# ventas.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.ventas import (
    crear_venta,
    generar_id_venta_rapida,
    generar_numero_factura,
    generar_numero_factura_unico,
    insertar_detalle_venta,
    insertar_venta,
    obtener_detalle_venta,
    obtener_todas_ventas,
    obtener_ultima_venta,
    obtener_ventas_por_cliente,
    obtener_ventas_por_id,
    obtener_ventas_por_numero_factura,
    obtener_ventas_rango_fechas,
)

# ------------------------------------------------------------------
# deudas.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.deudas import (
    actualizar_saldo_deuda,
    crear_deuda,
    generar_numero_factura_unico_deuda,
    insertar_deuda,
    insertar_detalle_deuda,
    obtener_detalle_deuda,
    obtener_deuda_por_id,
    obtener_deudas,
    obtener_deudas_abiertas,
    obtener_deudas_por_cliente,
    obtener_deudas_por_numero_factura,
    obtener_deudas_rango_fechas,
    obtener_historial_deudas,
    obtener_historial_deudas_por_deuda,
    registrar_pago,
    sumatoria_deudas,
)

# ------------------------------------------------------------------
# papelera.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.papelera import (
    eliminar_deuda,
    eliminar_venta,
    mover_deuda_a_papelera,
    mover_venta_a_papelera,
    obtener_deudas_papelera,
    obtener_papelera_deudas,
    obtener_papelera_ventas,
    obtener_ventas_papelera,
)

# ------------------------------------------------------------------
# historiales.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.historiales import (
    _ejecutar_historial_deuda,
    _ejecutar_historial_venta,
    obtener_historial_por_venta,
    obtener_historial_ventas,
    registrar_historial_deuda,
    registrar_historial_venta,
)

# ------------------------------------------------------------------
# ganancias.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.ganancias import (
    actualizar_cuentas,
    calcular_ganancia_dia,
    insertar_ganancia,
    obtener_ganancia_por_fecha,
    obtener_ganancias_rango_fechas,
)

# ------------------------------------------------------------------
# usuarios.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.usuarios import (
    actualizar_usuario,
    buscar_usuario,
    eliminar_usuario,
    insertar_usuario,
    obtener_usuarios,
    verificar_desarrollador,
    verificar_usuario,
)

# ------------------------------------------------------------------
# formateo.py
# ------------------------------------------------------------------
from retail.nucleo.base_datos.formateo import (
    formatear_inventario,
    formatear_venta,
    peso_colombiano,
)

# ===================================================================
# DB_NAME como property enlazada a config_db
# ===================================================================


class _ModuloBaseDatos(types.ModuleType):
    @property
    def DB_NAME(self) -> str:
        return config_db.nombre

    @DB_NAME.setter
    def DB_NAME(self, value: str) -> None:
        config_db.nombre = value


sys.modules[__name__].__class__ = _ModuloBaseDatos
