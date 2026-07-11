from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def pagadas(db: Any) -> Any:
    from retail.nucleo.servicios.deudas.servicio_pagadas import ServicioPagadas
    return ServicioPagadas


def _crear_deuda_pagada(db: Any, nombres: str, apellidos: str, doc: str, tel: str, producto: str, precio: float, costo: float, stock: int, cantidad: int) -> int:
    cid = insertar_cliente(db, nombres, apellidos, doc, tel)
    pid = insertar_producto(db, producto, precio, costo, stock)
    db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": cantidad}], usuario="test")
    with db.conexion() as conn:
        idd = conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]
    from retail.nucleo.servicios.deudas.servicio_facturas_deudas import ServicioFacturasDeudas
    ServicioFacturasDeudas.registrar_pago(idd, precio * cantidad, precio * cantidad, "test")
    return idd


class TestServicioPagadas:
    def test_contar_pagadas_sin_datos(self, pagadas: Any):
        assert pagadas.contar_pagadas() == 0

    def test_contar_pagadas_con_datos(self, pagadas: Any, db: Any):
        _crear_deuda_pagada(db, "Juan", "Perez", "11111", "3001111111", "Ron", 50000, 30000, 10, 2)
        assert pagadas.contar_pagadas() == 1

    def test_obtener_pagina_vacia(self, pagadas: Any):
        assert pagadas.obtener_pagina(0, 10) == []

    def test_obtener_pagina_con_datos(self, pagadas: Any, db: Any):
        _crear_deuda_pagada(db, "Maria", "Gomez", "22222", "3002222222", "Whisky", 120000, 80000, 5, 1)
        pagina = pagadas.obtener_pagina(0, 10)
        assert len(pagina) >= 1
        assert "id_deuda" in pagina[0]
        assert "cliente" in pagina[0]
        assert "total" in pagina[0]

    def test_calcular_total_pagado(self, pagadas: Any, db: Any):
        _crear_deuda_pagada(db, "Ana", "Lopez", "33333", "3003333333", "Cerveza", 3000, 2000, 50, 10)
        total = pagadas.calcular_total_pagado()
        assert total == 30000.0

    def test_obtener_lista_clientes(self, pagadas: Any, db: Any):
        _crear_deuda_pagada(db, "Carlos", "Ruiz", "44444", "3004444444", "Tequila", 80000, 50000, 10, 1)
        clientes = pagadas.obtener_lista_clientes()
        assert len(clientes) >= 1

    def test_obtener_detalles_para_pdf(self, pagadas: Any, db: Any):
        idd = _crear_deuda_pagada(db, "Luis", "Martinez", "55555", "3005555555", "Vodka", 40000, 20000, 10, 2)
        prods, cliente = pagadas.obtener_detalles_para_pdf(idd)
        assert len(prods) >= 1
        assert "Luis" in cliente
