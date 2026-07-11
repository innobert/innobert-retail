"""
ventas_service.py

Servicio que encapsula toda la lógica de negocio para el módulo de Ventas.
Incluye validación de stock, gestión del carrito, búsqueda de productos,
creación de ventas y obtención de datos de clientes.
"""

from retail.nucleo.base_datos import (
    obtener_productos,
    obtener_clientes,
    buscar_productos_por_nombre,
    crear_venta,
    actualizar_cuentas,
    obtener_conexion,           # Añadido para las nuevas funciones de paginación
)
from typing import List, Dict, Any, Optional, Tuple


class VentasServicio:
    """
    Servicio para operaciones de ventas.
    Todas las operaciones son estáticas o de instancia, pero no mantienen estado
    interno; reciben el carrito como parámetro.
    """

    @staticmethod
    def obtener_stock_actual(id_producto: int) -> Optional[int]:
        """
        Retorna el stock actual de un producto desde la base de datos.
        """
        productos = obtener_productos()
        for p in productos:
            if p[0] == id_producto:
                return p[4]
        return None

    @staticmethod
    def validar_cantidad(
        id_producto: int,
        cantidad_solicitada: int,
        carrito_actual: List[Dict[str, Any]]
    ) -> Tuple[bool, int, str]:
        """
        Valida si la cantidad solicitada está disponible.
        Retorna (válido, stock_disponible, mensaje).
        """
        stock_total = VentasServicio.obtener_stock_actual(id_producto)
        if stock_total is None:
            return False, 0, "No se pudo obtener el stock del producto."

        # Cantidad ya reservada en el carrito actual
        cantidad_reservada = sum(
            item["cantidad"] for item in carrito_actual
            if item["id_producto"] == id_producto
        )
        stock_disponible = stock_total - cantidad_reservada

        if cantidad_solicitada <= 0:
            return False, stock_disponible, "La cantidad debe ser mayor a cero."

        if cantidad_solicitada > stock_disponible:
            msg = (f"Stock disponible para agregar: {stock_disponible} unidades.\n"
                   f"Stock total: {stock_total} | Ya en carrito: {cantidad_reservada}")
            return False, stock_disponible, msg

        return True, stock_disponible, ""

    @staticmethod
    def agregar_al_carrito(
        carrito: List[Dict[str, Any]],
        producto_data: Dict[str, Any],
        cantidad: int,
        cliente_id: Optional[int],
        tipo_venta: str
    ) -> Tuple[List[Dict[str, Any]], str, Optional[Dict[str, Any]]]:
        """
        Agrega un producto al carrito si pasa la validación.
        Retorna (carrito_actualizado, mensaje, error_dict o None).
        """
        id_producto = producto_data["id_producto"]

        # Validar cantidad
        valido, stock, msg = VentasServicio.validar_cantidad(
            id_producto, cantidad, carrito
        )
        if not valido:
            return carrito, msg, {"error": msg, "producto": producto_data["producto"]}

        # Determinar nombre del cliente para el carrito
        cliente_carrito = ""
        if tipo_venta == "mayorista" and cliente_id:
            try:
                clientes = obtener_clientes()
                for c in clientes:
                    if c[0] == cliente_id:
                        cliente_carrito = f"{c[1]} {c[2]}"
                        break
            except Exception:
                pass

        # Verificar que no se duplique el mismo producto para el mismo cliente
        producto_en_carrito = any(
            item["producto"] == producto_data["producto"] and
            item["cliente"] == cliente_carrito
            for item in carrito
        )
        if producto_en_carrito:
            return carrito, "El producto ya está en el carrito.", {
                "error": "duplicado",
                "producto": producto_data["producto"]
            }

        # Agregar item
        nuevo_item = {
            "cliente": cliente_carrito,
            "cliente_id": cliente_id,
            "producto": producto_data["producto"],
            "id_producto": id_producto,
            "cantidad": cantidad,
            "precio": producto_data["precio"],
            "subtotal": cantidad * producto_data["precio"],
        }
        carrito.append(nuevo_item)
        return carrito, "", None

    @staticmethod
    def obtener_clientes_formateados() -> Tuple[List[str], Dict[str, int]]:
        """
        Retorna una lista de nombres de clientes y un diccionario
        que mapea nombre -> id_cliente.
        """
        clientes = obtener_clientes()
        nombres = [f"{c[1]} {c[2]}" for c in clientes]
        mapeo = {f"{c[1]} {c[2]}": c[0] for c in clientes}
        return nombres, mapeo

    @staticmethod
    def obtener_productos_para_busqueda(termino: str = "") -> List[Dict[str, Any]]:
        """
        Retorna lista de productos (como diccionarios) que coinciden con el término.
        Si termino está vacío, devuelve todos.
        """
        if not termino:
            productos = obtener_productos()
        else:
            productos = buscar_productos_por_nombre(termino)
        # Convertir a lista de diccionarios
        return [
            {
                "id_producto": p[0],
                "producto": p[1],
                "precio": p[2],
                "costo": p[3],
                "stock": p[4],
                "estado": p[5],
                "imagen": p[6],
            }
            for p in productos
        ]

    @staticmethod
    def calcular_total_carrito(carrito: List[Dict[str, Any]]) -> int:
        """
        Calcula el total del carrito sumando subtotales.
        """
        total = 0
        for item in carrito:
            try:
                total += float(item.get("subtotal", 0))
            except Exception:
                total += 0
        return int(total)

    @staticmethod
    def confirmar_venta(
        carrito: List[Dict[str, Any]],
        cliente_id: Optional[int],
        monto_recibido: float,
        usuario: str
    ) -> Dict[str, Any]:
        """
        Crea la venta en la base de datos usando el carrito actual.
        Retorna el resultado de crear_venta (id_ventas, total, vuelto).
        Lanza excepciones si hay errores.
        """
        if not carrito:
            raise ValueError("El carrito está vacío.")

        items = []
        for item in carrito:
            items.append({
                "id_producto": item["id_producto"],
                "cantidad": item["cantidad"],
                "precio": item["precio"]
            })

        # Llamar a la función de base de datos que ya maneja la transacción
        resultado = crear_venta(
            cliente_id=cliente_id,
            items=items,
            monto_recibido=monto_recibido,
            usuario=usuario
        )

        # Actualizar las cuentas de ganancias (puede moverse a un servicio aparte)
        actualizar_cuentas()

        return resultado

    @staticmethod
    def filtrar_clientes_por_texto(texto: str) -> List[Dict[str, Any]]:
        """
        Filtra clientes por coincidencia parcial en nombre o apellido.
        Retorna lista de diccionarios con id, nombres, apellidos.
        """
        texto_lower = texto.lower()
        clientes = obtener_clientes()
        resultado = []
        for c in clientes:
            nombre_completo = f"{c[1]} {c[2]}"
            if texto_lower in c[1].lower() or texto_lower in c[2].lower():
                resultado.append({
                    "id_cliente": c[0],
                    "nombres": c[1],
                    "apellidos": c[2],
                    "nombre_completo": nombre_completo
                })
        return resultado

    @staticmethod
    def obtener_cliente_por_nombre_completo(nombre_completo: str) -> Optional[Dict[str, Any]]:
        """
        Busca un cliente por su nombre completo exacto.
        Retorna diccionario con id, nombres, apellidos o None.
        """
        clientes = obtener_clientes()
        for c in clientes:
            if f"{c[1]} {c[2]}" == nombre_completo:
                return {
                    "id_cliente": c[0],
                    "nombres": c[1],
                    "apellidos": c[2],
                    "nombre_completo": nombre_completo
                }
        return None

    # ----------------------------------------------------------------------
    # Nuevos métodos para paginación con carga bajo demanda
    # ----------------------------------------------------------------------

    @staticmethod
    def obtener_productos_paginado(
        offset: int,
        limit: int,
        filtro: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Obtiene una página de productos desde la base de datos.
        offset: número de registros a saltar
        limit: cantidad de registros a obtener
        filtro: texto para filtrar por nombre (coincidencia parcial, case-insensitive)
        """
        conn = obtener_conexion()
        cursor = conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT * FROM inventario WHERE producto LIKE ? ORDER BY id_producto LIMIT ? OFFSET ?",
                (f"%{filtro}%", limit, offset)
            )
        else:
            cursor.execute(
                "SELECT * FROM inventario ORDER BY id_producto LIMIT ? OFFSET ?",
                (limit, offset)
            )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id_producto": r[0],
                "producto": r[1],
                "precio": r[2],
                "costo": r[3],
                "stock": r[4],
                "estado": r[5],
                "imagen": r[6],
            }
            for r in rows
        ]

    @staticmethod
    def contar_productos(filtro: str = "") -> int:
        """
        Retorna el número total de productos que coinciden con el filtro.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT COUNT(*) FROM inventario WHERE producto LIKE ?",
                (f"%{filtro}%",)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM inventario")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def obtener_nombres_productos_para_busqueda(filtro: str = "") -> List[str]:
        """
        Retorna solo los nombres de productos que coinciden con el filtro.
        Útil para actualizar el combobox de búsqueda sin cargar datos completos.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT producto FROM inventario WHERE producto LIKE ? ORDER BY producto",
                (f"%{filtro}%",)
            )
        else:
            cursor.execute("SELECT producto FROM inventario ORDER BY producto")
        nombres = [row[0] for row in cursor.fetchall()]
        conn.close()
        return nombres

    # ----------------------------------------------------------------------
    # Método auxiliar para obtener nombre del cliente por ID
    # ----------------------------------------------------------------------
    @staticmethod
    def obtener_nombre_cliente_por_id(cliente_id: int) -> Optional[str]:
        """
        Retorna el nombre completo de un cliente por su ID.
        """
        clientes = obtener_clientes()
        for c in clientes:
            if c[0] == cliente_id:
                return f"{c[1]} {c[2]}"
        return None