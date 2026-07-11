"""Estado compartido mutable para la configuración de la base de datos.

Permite que las pruebas sobrescriban la ruta de la base de datos
sin necesidad de modificar variables de módulo directamente.
"""

from retail.nucleo.configuraciones import obtener_ruta_base_datos


class _ConfiguracionBaseDeDatos:
    nombre = obtener_ruta_base_datos()


config_db = _ConfiguracionBaseDeDatos()
