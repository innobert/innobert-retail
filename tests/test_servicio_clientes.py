from __future__ import annotations

from pathlib import Path
from typing import Any
import pytest


@pytest.fixture
def clientes_servicio(db: Any) -> Any:
    """Retorna la clase ClientesServicio con BD lista."""
    from retail.nucleo.servicios.clientes.servicio_clientes import ClientesServicio
    return ClientesServicio


class TestObtenerTodosClientes:
    def test_sin_clientes_retorna_vacio(self, clientes_servicio: Any):
        assert clientes_servicio.obtener_todos_clientes() == []

    def test_con_clientes_retorna_lista(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Carlos", "Perez", "12345", "3001112233", "Norte")
        _insertar_cliente(db, "Maria", "Gomez", "67890", "3004445566", "Sur")
        clientes = clientes_servicio.obtener_todos_clientes()
        assert len(clientes) == 2
        assert clientes[0]["nombres"] == "Carlos"
        assert clientes[1]["nombres"] == "Maria"


class TestAgregarCliente:
    def test_agregar_exitoso(self, clientes_servicio: Any, db: Any):
        exito, mensaje = clientes_servicio.agregar_cliente("Luis", "Martinez", "11111", "3007778899", "Centro")
        assert exito is True
        assert "correctamente" in mensaje
        clientes = clientes_servicio.obtener_todos_clientes()
        assert len(clientes) == 1
        assert clientes[0]["nombres"] == "Luis"

    def test_agregar_sin_nombres(self, clientes_servicio: Any):
        exito, mensaje = clientes_servicio.agregar_cliente("", "Martinez", "11111", "3007778899", "Centro")
        assert exito is False
        assert "obligatorios" in mensaje

    def test_agregar_sin_apellidos(self, clientes_servicio: Any):
        exito, mensaje = clientes_servicio.agregar_cliente("Luis", "", "11111", "3007778899", "Centro")
        assert exito is False

    def test_agregar_sin_cedula(self, clientes_servicio: Any):
        exito, mensaje = clientes_servicio.agregar_cliente("Luis", "Martinez", "", "3007778899", "Centro")
        assert exito is False

    def test_agregar_sin_celular(self, clientes_servicio: Any):
        exito, mensaje = clientes_servicio.agregar_cliente("Luis", "Martinez", "11111", "", "Centro")
        assert exito is False

    def test_agregar_sin_zona(self, clientes_servicio: Any):
        exito, mensaje = clientes_servicio.agregar_cliente("Luis", "Martinez", "11111", "3007778899", "")
        assert exito is False

    def test_agregar_cedula_duplicada(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Pedro", "Lopez", "99999", "3001110001", "Este")
        exito, mensaje = clientes_servicio.agregar_cliente("Otro", "Cliente", "99999", "3001110002", "Oeste")
        assert exito is False
        assert "cédula" in mensaje or "cedula" in mensaje

    def test_agregar_celular_duplicado(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Pedro", "Lopez", "88888", "3001110001", "Este")
        exito, mensaje = clientes_servicio.agregar_cliente("Otro", "Cliente", "88889", "3001110001", "Oeste")
        assert exito is False
        assert "celular" in mensaje


class TestActualizarCliente:
    def test_actualizar_nombres(self, clientes_servicio: Any, db: Any):
        cid = _insertar_cliente(db, "Juan", "Ramirez", "22222", "3002223344", "Norte")
        exito, mensaje = clientes_servicio.actualizar_cliente(cid, "nombres", "Juan Carlos")
        assert exito is True
        cliente = clientes_servicio.obtener_cliente_por_id(cid)
        assert cliente["nombres"] == "Juan Carlos"

    def test_actualizar_apellidos(self, clientes_servicio: Any, db: Any):
        cid = _insertar_cliente(db, "Ana", "Lopez", "33333", "3003334455", "Sur")
        exito, mensaje = clientes_servicio.actualizar_cliente(cid, "apellidos", "Lopez Ruiz")
        assert exito is True
        cliente = clientes_servicio.obtener_cliente_por_id(cid)
        assert cliente["apellidos"] == "Lopez Ruiz"

    def test_actualizar_cedula(self, clientes_servicio: Any, db: Any):
        cid = _insertar_cliente(db, "Luis", "Garcia", "44444", "3004445566", "Centro")
        exito, mensaje = clientes_servicio.actualizar_cliente(cid, "cedula", "55555")
        assert exito is True
        cliente = clientes_servicio.obtener_cliente_por_id(cid)
        assert str(cliente["cedula"]) == "55555"

    def test_actualizar_celular(self, clientes_servicio: Any, db: Any):
        cid = _insertar_cliente(db, "Sofia", "Mora", "66666", "3006667788", "Oeste")
        exito, mensaje = clientes_servicio.actualizar_cliente(cid, "celular", "3009998877")
        assert exito is True
        cliente = clientes_servicio.obtener_cliente_por_id(cid)
        assert str(cliente["celular"]) == "3009998877"

    def test_actualizar_zona(self, clientes_servicio: Any, db: Any):
        cid = _insertar_cliente(db, "Pedro", "Sanchez", "77777", "3007778899", "Norte")
        exito, mensaje = clientes_servicio.actualizar_cliente(cid, "zona", "Occidente")
        assert exito is True
        cliente = clientes_servicio.obtener_cliente_por_id(cid)
        assert cliente["zona"] == "Occidente"

    def test_actualizar_campo_invalido(self, clientes_servicio: Any):
        exito, mensaje = clientes_servicio.actualizar_cliente(1, "edad", "30")
        assert exito is False
        assert "no válido" in mensaje

    def test_actualizar_cedula_duplicada(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Primero", "Uno", "11100", "3001110001", "A")
        cid = _insertar_cliente(db, "Segundo", "Dos", "22200", "3002220002", "B")
        exito, mensaje = clientes_servicio.actualizar_cliente(cid, "cedula", "11100")
        assert exito is False
        assert "cédula" in mensaje or "cedula" in mensaje

    def test_actualizar_celular_duplicado(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Primero", "Uno", "11101", "3001110001", "A")
        cid = _insertar_cliente(db, "Segundo", "Dos", "22201", "3002220002", "B")
        exito, mensaje = clientes_servicio.actualizar_cliente(cid, "celular", "3001110001")
        assert exito is False
        assert "celular" in mensaje

    def test_actualizar_cliente_inexistente(self, clientes_servicio: Any):
        exito, mensaje = clientes_servicio.actualizar_cliente(9999, "nombres", "Test")
        assert exito is True  # actualizar_cliente no falla si no existe


class TestEliminarCliente:
    def test_eliminar_exitoso(self, clientes_servicio: Any, db: Any):
        cid = _insertar_cliente(db, "Laura", "Castro", "88888", "3008889900", "Este")
        exito, mensaje = clientes_servicio.eliminar_cliente(cid)
        assert exito is True
        assert clientes_servicio.obtener_cliente_por_id(cid) is None

    def test_eliminar_inexistente(self, clientes_servicio: Any):
        exito, mensaje = clientes_servicio.eliminar_cliente(9999)
        assert exito is True


class TestObtenerClientePorId:
    def test_cliente_existente(self, clientes_servicio: Any, db: Any):
        cid = _insertar_cliente(db, "Roberto", "Gimenez", "12321", "3001232123", "Norte")
        cliente = clientes_servicio.obtener_cliente_por_id(cid)
        assert cliente is not None
        assert cliente["nombres"] == "Roberto"
        assert cliente["apellidos"] == "Gimenez"

    def test_cliente_inexistente(self, clientes_servicio: Any):
        cliente = clientes_servicio.obtener_cliente_por_id(9999)
        assert cliente is None


class TestContarClientes:
    def test_sin_clientes(self, clientes_servicio: Any):
        assert clientes_servicio.contar_clientes() == 0

    def test_todos_los_clientes(self, clientes_servicio: Any, db: Any):
        for i in range(5):
            _insertar_cliente(db, f"Nombre{i}", "Apellido", f"1000{i}", f"300000000{i}", "Zona")
        assert clientes_servicio.contar_clientes() == 5

    def test_con_filtro(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Alan", "Turing", "11110", "3001111110", "Norte")
        _insertar_cliente(db, "Alanis", "Morris", "11111", "3001111111", "Sur")
        _insertar_cliente(db, "Alberto", "Castro", "11112", "3001111112", "Este")
        _insertar_cliente(db, "Beatriz", "Lopez", "11113", "3001111113", "Oeste")
        assert clientes_servicio.contar_clientes(filtro="Alan") == 2
        assert clientes_servicio.contar_clientes(filtro="Alberto") == 1
        assert clientes_servicio.contar_clientes(filtro="Turing") == 1
        assert clientes_servicio.contar_clientes(filtro="zzzz") == 0


class TestObtenerClientesPaginado:
    def test_obtener_clientes_paginado(self, clientes_servicio: Any, db: Any):
        for i in range(10):
            _insertar_cliente(db, f"Cliente{i}", "Test", f"2000{i}", f"301000000{i}", "Norte")
        pagina = clientes_servicio.obtener_clientes_paginado(0, 3)
        assert len(pagina) == 3
        assert pagina[0]["nombres"] == "Cliente0"

    def test_pagina_vacia(self, clientes_servicio: Any):
        pagina = clientes_servicio.obtener_clientes_paginado(0, 10)
        assert pagina == []

    def test_con_filtro(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Pepe", "Martinez", "30001", "3100000001", "A")
        _insertar_cliente(db, "Pepe", "Garcia", "30002", "3100000002", "B")
        _insertar_cliente(db, "Jose", "Lopez", "30003", "3100000003", "C")
        pagina = clientes_servicio.obtener_clientes_paginado(0, 10, filtro="Pepe")
        assert len(pagina) == 2

    def test_filtro_sin_resultados(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Solo", "Uno", "40001", "3200000001", "Z")
        pagina = clientes_servicio.obtener_clientes_paginado(0, 10, filtro="inexistente")
        assert pagina == []


class TestObtenerNombresClientesParaBusqueda:
    def test_sin_filtro(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Carlos", "Perez", "50001", "3300000001", "Norte")
        _insertar_cliente(db, "Ana", "Lopez", "50002", "3300000002", "Sur")
        nombres = clientes_servicio.obtener_nombres_clientes_para_busqueda()
        assert len(nombres) == 2
        assert "Ana Lopez" in nombres
        assert "Carlos Perez" in nombres

    def test_con_filtro(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Fernanda", "Torres", "50003", "3300000003", "Este")
        _insertar_cliente(db, "Fernando", "Rios", "50004", "3300000004", "Oeste")
        _insertar_cliente(db, "Luis", "Mora", "50005", "3300000005", "Centro")
        nombres = clientes_servicio.obtener_nombres_clientes_para_busqueda("Fernan")
        assert len(nombres) == 2
        assert "Fernanda Torres" in nombres
        assert "Fernando Rios" in nombres

    def test_filtro_sin_resultados(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Solo", "Uno", "50006", "3300000006", "Z")
        nombres = clientes_servicio.obtener_nombres_clientes_para_busqueda("zzzz")
        assert nombres == []

    def test_filtro_por_apellido(self, clientes_servicio: Any, db: Any):
        _insertar_cliente(db, "Maria", "Gomez", "50007", "3300000007", "A")
        _insertar_cliente(db, "Pedro", "Gomez", "50008", "3300000008", "B")
        _insertar_cliente(db, "Luis", "Perez", "50009", "3300000009", "C")
        nombres = clientes_servicio.obtener_nombres_clientes_para_busqueda("Gomez")
        assert len(nombres) == 2


def _insertar_cliente(db: Any, nombres: str, apellidos: str, cedula: str, celular: str, zona: str) -> int:
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nombres, apellidos, cedula, celular, zona) VALUES (?, ?, ?, ?, ?)",
            (nombres, apellidos, cedula, celular, zona),
        )
        return cursor.lastrowid
