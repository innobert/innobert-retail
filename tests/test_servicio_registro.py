from __future__ import annotations

import hashlib
from typing import Any
from unittest.mock import patch
import pytest


@pytest.fixture
def db_limpia(db: Any) -> Any:
    """Elimina el usuario 'prueba' que crear_tablas() inserta por defecto."""
    with db.conexion() as conn:
        conn.execute("DELETE FROM usuarios WHERE usuario = ?", ("prueba",))
    return db


@pytest.fixture
def registro(db_limpia: Any) -> Any:
    """Retorna la clase ServicioRegistro con BD limpia."""
    from retail.nucleo.servicios.sesion.servicio_registro import ServicioRegistro
    return ServicioRegistro


class TestRegistrarUsuario:
    def test_registro_exitoso(self, registro: Any, db_limpia: Any):
        assert registro.registrar_usuario("admin", "123456") is True
        usuarios = _obtener_usuarios_bd(db_limpia)
        assert len(usuarios) == 1
        assert usuarios[0][0] == "admin"

    def test_registro_guarda_hash_contrasena(self, registro: Any, db_limpia: Any):
        registro.registrar_usuario("admin", "123456")
        usuarios = _obtener_usuarios_bd(db_limpia)
        hash_esperado = hashlib.sha256("123456".encode()).hexdigest()
        assert usuarios[0][1] == hash_esperado

    def test_registro_con_dias_licencia(self, registro: Any, db_limpia: Any):
        registro.registrar_usuario("admin", "123456", dias_licencia=60)
        usuarios = _obtener_usuarios_bd(db_limpia)
        assert len(usuarios) == 1

    def test_usuario_vacio_raises(self, registro: Any):
        with pytest.raises(ValueError, match="requeridos"):
            registro.registrar_usuario("", "123456")

    def test_contrasena_vacia_raises(self, registro: Any):
        with pytest.raises(ValueError, match="requeridos"):
            registro.registrar_usuario("admin", "")

    def test_usuario_corto_raises(self, registro: Any):
        with pytest.raises(ValueError, match="3 caracteres"):
            registro.registrar_usuario("ab", "123456")

    def test_contrasena_corta_raises(self, registro: Any):
        with pytest.raises(ValueError, match="6 caracteres"):
            registro.registrar_usuario("admin", "12345")


class TestObtenerTodosUsuarios:
    def test_sin_usuarios_retorna_vacio(self, registro: Any):
        assert registro.obtener_todos_usuarios() == []

    def test_con_usuarios_retorna_lista(self, registro: Any):
        registro.registrar_usuario("admin", "123456")
        registro.registrar_usuario("empleado", "123456")
        usuarios = registro.obtener_todos_usuarios()
        assert len(usuarios) == 2
        assert usuarios[0]["usuario"] == "admin"

    def test_excluir_desarrollador(self, registro: Any, db_limpia: Any):
        _insertar_usuario_bd(db_limpia, "innobertdev", "hash", "2025-01-01", "2025-12-31", "s1")
        registro.registrar_usuario("admin", "123456")
        usuarios = registro.obtener_todos_usuarios(excluir_desarrollador=True)
        assert len(usuarios) == 1
        assert usuarios[0]["usuario"] == "admin"

    def test_incluir_desarrollador(self, registro: Any, db_limpia: Any):
        _insertar_usuario_bd(db_limpia, "innobertdev", "hash", "2025-01-01", "2025-12-31", "s1")
        registro.registrar_usuario("admin", "123456")
        usuarios = registro.obtener_todos_usuarios(excluir_desarrollador=False)
        assert len(usuarios) == 2

    def test_usuarios_contienen_dias_restantes(self, registro: Any):
        registro.registrar_usuario("admin", "123456")
        usuarios = registro.obtener_todos_usuarios()
        assert "dias_restantes" in usuarios[0]
        assert usuarios[0]["dias_restantes"] > 0


class TestActualizarUsuario:
    def test_actualizar_nombre(self, registro: Any, db_limpia: Any):
        registro.registrar_usuario("admin", "123456")
        assert registro.actualizar_usuario("admin", "superadmin") is True
        usuarios = _obtener_usuarios_bd(db_limpia)
        assert any(u[0] == "superadmin" for u in usuarios)

    def test_actualizar_nombre_y_contrasena(self, registro: Any, db_limpia: Any):
        registro.registrar_usuario("admin", "123456")
        assert registro.actualizar_usuario("admin", "superadmin", "654321") is True
        usuarios = _obtener_usuarios_bd(db_limpia)
        admin = [u for u in usuarios if u[0] == "superadmin"][0]
        hash_esperado = hashlib.sha256("654321".encode()).hexdigest()
        assert admin[1] == hash_esperado

    def test_nuevo_usuario_vacio_raises(self, registro: Any):
        registro.registrar_usuario("admin", "123456")
        with pytest.raises(ValueError, match="vacío"):
            registro.actualizar_usuario("admin", "")

    def test_contrasena_corta_raises(self, registro: Any):
        registro.registrar_usuario("admin", "123456")
        with pytest.raises(ValueError, match="6 caracteres"):
            registro.actualizar_usuario("admin", "admin", "123")


class TestRenovarSuscripcion:
    @patch("retail.sesion.core.servicio_registro.ServicioLicencias.renovar_licencia")
    def test_delega_a_servicio_licencias(self, mock_renovar, registro: Any):
        mock_renovar.return_value = True
        assert registro.renovar_suscripcion("admin") is True
        mock_renovar.assert_called_once_with("admin", 30)

    @patch("retail.sesion.core.servicio_registro.ServicioLicencias.renovar_licencia")
    def test_delega_con_dias_personalizados(self, mock_renovar, registro: Any):
        mock_renovar.return_value = True
        assert registro.renovar_suscripcion("admin", dias=60) is True
        mock_renovar.assert_called_once_with("admin", 60)

    @patch("retail.sesion.core.servicio_registro.ServicioLicencias.renovar_licencia")
    def test_retorna_false_si_servicio_falla(self, mock_renovar, registro: Any):
        mock_renovar.return_value = False
        assert registro.renovar_suscripcion("admin") is False


class TestEliminarUsuario:
    def test_eliminar_exitoso(self, registro: Any, db_limpia: Any):
        registro.registrar_usuario("admin", "123456")
        assert registro.eliminar_usuario("admin") is True
        usuarios = _obtener_usuarios_bd(db_limpia)
        assert len(usuarios) == 0

    def test_eliminar_verificar_bd(self, registro: Any, db_limpia: Any):
        registro.registrar_usuario("admin", "123456")
        registro.registrar_usuario("empleado", "123456")
        registro.eliminar_usuario("admin")
        usuarios = _obtener_usuarios_bd(db_limpia)
        assert len(usuarios) == 1
        assert usuarios[0][0] == "empleado"


def _obtener_usuarios_bd(db: Any) -> list:
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT usuario, contrasena, fecha_inicio, fecha_fin, serial FROM usuarios"
        )
        return cursor.fetchall()


def _insertar_usuario_bd(
    db: Any, usuario: str, contrasena: str, fecha_inicio: str, fecha_fin: str, serial: str
) -> None:
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
            (usuario, contrasena, fecha_inicio, fecha_fin, serial),
        )
