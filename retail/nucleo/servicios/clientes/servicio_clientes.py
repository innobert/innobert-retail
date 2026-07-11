# retail/nucleo/servicios/clientes/servicio_clientes.py
"""
Servicio para la gestión de clientes.

Responsabilidades:
- CRUD completo de clientes (crear, leer, actualizar, eliminar).
- Paginación de clientes (carga bajo demanda).
- Búsqueda y autocompletado.
- Validación de campos (cédula y celular únicos).

Autor: InnobertDev
Fecha: Mayo 2026
"""

from typing import List, Dict, Any, Tuple, Optional
from retail.nucleo.base_datos import (
    obtener_clientes,
    insertar_cliente,
    eliminar_cliente,
    actualizar_cliente,
    obtener_conexion,
)


class ClientesServicio:
    """Servicio para operaciones de clientes."""

    # ------------------------------------------------------------------
    # CRUD BÁSICO
    # ------------------------------------------------------------------

    @staticmethod
    def obtener_todos_clientes() -> List[Dict[str, Any]]:
        """Retorna lista de todos los clientes como diccionarios."""
        clientes = obtener_clientes()
        return [
            {
                "id_cliente": c[0],
                "nombres": c[1],
                "apellidos": c[2],
                "cedula": c[3],
                "celular": c[4],
                "zona": c[5],
            }
            for c in clientes
        ]

    @staticmethod
    def agregar_cliente(
        nombres: str,
        apellidos: str,
        cedula: str,
        celular: str,
        zona: str
    ) -> Tuple[bool, str]:
        """
        Agrega un nuevo cliente. Valida que cédula y celular no estén duplicados.
        """
        # Validar campos
        if not all([nombres, apellidos, cedula, celular, zona]):
            return False, "Todos los campos son obligatorios."

        # Verificar duplicados (cédula y celular únicos)
        for c in ClientesServicio.obtener_todos_clientes():
            if c["cedula"] and str(c["cedula"]) == str(cedula):
                return False, f"Ya existe un cliente con la cédula {cedula}."
            if c["celular"] and str(c["celular"]) == str(celular):
                return False, f"Ya existe un cliente con el celular {celular}."

        try:
            insertar_cliente(nombres, apellidos, cedula, celular, zona)
            return True, "Cliente agregado correctamente."
        except Exception as e:
            return False, f"Error al agregar cliente: {e}"

    @staticmethod
    def actualizar_cliente(id_cliente: int, campo: str, valor: str) -> Tuple[bool, str]:
        """
        Actualiza un campo específico de un cliente.
        Campos válidos: nombres, apellidos, cedula, celular, zona.
        """
        campos_validos = ["nombres", "apellidos", "cedula", "celular", "zona"]
        if campo not in campos_validos:
            return False, f"Campo '{campo}' no válido."

        # Si actualiza cédula o celular, verificar unicidad
        if campo in ("cedula", "celular"):
            valor_str = str(valor)
            for c in ClientesServicio.obtener_todos_clientes():
                if c["id_cliente"] == id_cliente:
                    continue
                if campo == "cedula" and c["cedula"] and str(c["cedula"]) == valor_str:
                    return False, f"Ya existe otro cliente con la cédula {valor_str}."
                if campo == "celular" and c["celular"] and str(c["celular"]) == valor_str:
                    return False, f"Ya existe otro cliente con el celular {valor_str}."

        try:
            actualizar_cliente(id_cliente, campo, valor)
            return True, "Cliente actualizado correctamente."
        except Exception as e:
            return False, f"Error al actualizar: {e}"

    @staticmethod
    def eliminar_cliente(id_cliente: int) -> Tuple[bool, str]:
        """Elimina un cliente por su ID."""
        try:
            eliminar_cliente(id_cliente)
            return True, "Cliente eliminado correctamente."
        except Exception as e:
            return False, f"Error al eliminar cliente: {e}"

    @staticmethod
    def obtener_cliente_por_id(id_cliente: int) -> Optional[Dict[str, Any]]:
        """Retorna un cliente por su ID, o None si no existe."""
        for c in ClientesServicio.obtener_todos_clientes():
            if c["id_cliente"] == id_cliente:
                return c
        return None

    # ------------------------------------------------------------------
    # PAGINACIÓN Y BÚSQUEDA
    # ------------------------------------------------------------------

    @staticmethod
    def contar_clientes(filtro: str = "") -> int:
        """
        Retorna el número total de clientes que coinciden con el filtro
        (coincidencia parcial en nombres o apellidos).
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        if filtro:
            cursor.execute("""
                SELECT COUNT(*) FROM clientes
                WHERE nombres || ' ' || apellidos LIKE ?
            """, (f"%{filtro}%",))
        else:
            cursor.execute("SELECT COUNT(*) FROM clientes")
        total = cursor.fetchone()[0]
        conexion.close()
        return total

    @staticmethod
    def obtener_clientes_paginado(
        offset: int,
        limit: int,
        filtro: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Obtiene una página de clientes ordenada por ID ascendente.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        if filtro:
            cursor.execute("""
                SELECT id_cliente, nombres, apellidos, cedula, celular, zona
                FROM clientes
                WHERE nombres || ' ' || apellidos LIKE ?
                ORDER BY id_cliente
                LIMIT ? OFFSET ?
            """, (f"%{filtro}%", limit, offset))
        else:
            cursor.execute("""
                SELECT id_cliente, nombres, apellidos, cedula, celular, zona
                FROM clientes
                ORDER BY id_cliente
                LIMIT ? OFFSET ?
            """, (limit, offset))
        filas = cursor.fetchall()
        conexion.close()
        return [
            {
                "id_cliente": f[0],
                "nombres": f[1],
                "apellidos": f[2],
                "cedula": f[3],
                "celular": f[4],
                "zona": f[5],
            }
            for f in filas
        ]

    @staticmethod
    def obtener_nombres_clientes_para_busqueda(filtro: str = "") -> List[str]:
        """
        Retorna nombres completos de clientes que coinciden con el filtro,
        para autocompletado en el combobox.
        """
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        if filtro:
            cursor.execute("""
                SELECT nombres || ' ' || apellidos
                FROM clientes
                WHERE nombres || ' ' || apellidos LIKE ?
                ORDER BY nombres
            """, (f"%{filtro}%",))
        else:
            cursor.execute("""
                SELECT nombres || ' ' || apellidos
                FROM clientes
                ORDER BY nombres
            """)
        nombres = [f[0] for f in cursor.fetchall()]
        conexion.close()
        return nombres