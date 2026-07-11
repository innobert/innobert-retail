from __future__ import annotations

import datetime
from typing import Any
import pytest


@pytest.fixture
def licencias(db: Any) -> Any:
    from retail.nucleo.servicios.sesion.servicio_licencias import ServicioLicencias
    return ServicioLicencias


class TestGenerarLicencia:
    def test_generar_licencia_default(self, licencias: Any):
        licencia = licencias.generar_licencia("usuario_test")
        assert licencia["usuario"] == "usuario_test"
        assert licencia["dias"] == 30
        assert isinstance(licencia["serial"], str)
        assert len(licencia["serial"]) > 0
        assert licencia["fecha_inicio"] == datetime.datetime.now().strftime("%Y-%m-%d")

    def test_generar_licencia_dias_personalizados(self, licencias: Any):
        licencia = licencias.generar_licencia("otro_usuario", dias=60)
        assert licencia["usuario"] == "otro_usuario"
        assert licencia["dias"] == 60


class TestCrearLicenciaEnBD:
    def test_crear_licencia_exitosa(self, licencias: Any, db: Any):
        _crear_usuario(db, "test_user")
        licencia = licencias.generar_licencia("test_user")
        exito = licencias.crear_licencia_en_bd(
            licencia["usuario"], licencia["fecha_inicio"], licencia["fecha_fin"], licencia["serial"],
        )
        assert exito is True
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT usuario FROM usuarios WHERE usuario = ?", ("test_user",))
            assert cursor.fetchone() is not None

    def test_crear_licencia_actualiza_existente(self, licencias: Any, db: Any):
        _crear_usuario(db, "user")
        licencias.crear_licencia_en_bd("user", "2020-01-01", "2020-01-31", "serial1")
        exito = licencias.crear_licencia_en_bd("user", "2021-01-01", "2021-01-31", "serial2")
        assert exito is True
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT serial FROM usuarios WHERE usuario = ?", ("user",))
            assert cursor.fetchone()[0] == "serial2"


class TestValidarLicencia:
    def test_licencia_valida(self, licencias: Any, db: Any):
        _crear_licencia(db, "usuario", "2025-01-01", "2099-12-31", "serial-abc")
        valida, mensaje = licencias.validar_licencia("usuario", "serial-abc")
        assert valida is True
        assert mensaje == "Licencia v\u00e1lida."

    def test_licencia_expirada(self, licencias: Any, db: Any):
        _crear_licencia(db, "expirado", "2020-01-01", "2020-02-01", "serial-vencido")
        valida, mensaje = licencias.validar_licencia("expirado", "serial-vencido")
        assert valida is False
        assert "vencida" in mensaje

    def test_licencia_no_encontrada(self, licencias: Any):
        valida, mensaje = licencias.validar_licencia("no_existe", "serial-falso")
        assert valida is False
        assert mensaje == "Licencia no encontrada."


class TestObtenerLicencia:
    def test_obtener_licencia_existente(self, licencias: Any, db: Any):
        _crear_licencia(db, "test_user", "2025-01-01", "2025-06-01", "serial-xyz")
        licencia = licencias.obtener_licencia("test_user")
        assert licencia is not None
        assert licencia["usuario"] == "test_user"
        assert licencia["serial"] == "serial-xyz"
        assert licencia["fecha_inicio"] == "2025-01-01"
        assert licencia["fecha_fin"] == "2025-06-01"

    def test_obtener_licencia_inexistente(self, licencias: Any):
        assert licencias.obtener_licencia("no_existe") is None


class TestRenovarLicencia:
    def test_renovar_licencia(self, licencias: Any, db: Any):
        _crear_licencia(db, "usuario", "2020-01-01", "2020-02-01", "old-serial")
        exito = licencias.renovar_licencia("usuario")
        assert exito is True
        licencia = licencias.obtener_licencia("usuario")
        assert licencia is not None
        assert licencia["serial"] != "old-serial"

    def test_renovar_licencia_dias_personalizados(self, licencias: Any, db: Any):
        _crear_licencia(db, "otro", "2020-01-01", "2020-02-01", "old-serial")
        exito = licencias.renovar_licencia("otro", dias=15)
        assert exito is True
        licencia = licencias.obtener_licencia("otro")
        assert licencia is not None


class TestDiasRestantes:
    def test_dias_restantes_positivos(self, licencias: Any, db: Any):
        _crear_licencia(db, "vigente", "2025-01-01", "2099-12-31", "serial-futuro")
        dias = licencias.dias_restantes("vigente")
        assert dias > 0

    def test_dias_restantes_expirados(self, licencias: Any, db: Any):
        _crear_licencia(db, "expirado", "2020-01-01", "2020-02-01", "serial-pasado")
        dias = licencias.dias_restantes("expirado")
        assert dias == 0

    def test_dias_restantes_sin_licencia(self, licencias: Any):
        assert licencias.dias_restantes("sin_licencia") == 0


class TestLicenciaProximaAVencer:
    def test_proxima_a_vencer_dentro_alerta(self, licencias: Any, db: Any):
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        _crear_licencia(db, "cerca", "2025-01-01", fecha_fin, "serial-proximo")
        assert licencias.licencia_proxima_a_vencer("cerca", dias_alerta=7) is True

    def test_proxima_a_vencer_fuera_alerta(self, licencias: Any, db: Any):
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        _crear_licencia(db, "lejos", "2025-01-01", fecha_fin, "serial-lejano")
        assert licencias.licencia_proxima_a_vencer("lejos", dias_alerta=7) is False

    def test_proxima_a_vencer_sin_licencia(self, licencias: Any):
        assert licencias.licencia_proxima_a_vencer("sin_licencia") is False


class TestObtenerEstadoLicencia:
    def test_estado_no_encontrada(self, licencias: Any):
        estado = licencias.obtener_estado_licencia("inexistente")
        assert estado["estado"] == "no_encontrada"
        assert estado["dias_restantes"] == 0

    def test_estado_vencido_hoy(self, licencias: Any, db: Any):
        fecha_fin = datetime.datetime.now().strftime("%Y-%m-%d")
        _crear_licencia(db, "hoy", "2025-01-01", fecha_fin, "serial-hoy")
        estado = licencias.obtener_estado_licencia("hoy")
        assert estado["estado"] == "vencido_hoy"
        assert estado["dias_restantes"] == 0
        assert "hoy" in estado["mensaje"]

    def test_estado_proxima_a_vencer(self, licencias: Any, db: Any):
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        _crear_licencia(db, "prox", "2025-01-01", fecha_fin, "serial-prox")
        estado = licencias.obtener_estado_licencia("prox")
        assert estado["estado"] == "proxima_a_vencer"
        assert 0 < estado["dias_restantes"] <= 7
        assert "serial" in estado

    def test_estado_vigente(self, licencias: Any, db: Any):
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        _crear_licencia(db, "vigente", "2025-01-01", fecha_fin, "serial-vigente")
        estado = licencias.obtener_estado_licencia("vigente")
        assert estado["estado"] == "vigente"
        assert estado["dias_restantes"] > 7
        assert "serial" in estado


def _crear_usuario(db: Any, usuario: str) -> None:
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO usuarios (usuario, contrasena) VALUES (?, ?)",
            (usuario, "test_password"),
        )


def _crear_licencia(db: Any, usuario: str, fecha_inicio: str, fecha_fin: str, serial: str) -> None:
    _crear_usuario(db, usuario)
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET fecha_inicio = ?, fecha_fin = ?, serial = ? WHERE usuario = ?",
            (fecha_inicio, fecha_fin, serial, usuario),
        )
