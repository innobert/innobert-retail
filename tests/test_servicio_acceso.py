from __future__ import annotations

import hashlib
import json
from typing import Any
import pytest

from retail.nucleo.cifrado import cifrar


@pytest.fixture
def servicio_acceso(db: Any) -> Any:
    from retail.nucleo.servicios.sesion.servicio_acceso import ServicioAcceso
    return ServicioAcceso


class TestAutenticarUsuario:
    def test_credenciales_vacias(self, servicio_acceso: Any):
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("", "")
        assert exito is False
        assert "incompletas" in mensaje

    def test_credenciales_solo_usuario(self, servicio_acceso: Any):
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("user", "")
        assert exito is False
        assert "incompletas" in mensaje

    def test_credenciales_solo_contrasena(self, servicio_acceso: Any):
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("", "pass")
        assert exito is False
        assert "incompletas" in mensaje

    def test_usuario_reservado_admin(self, servicio_acceso: Any):
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("admin", "cualquiera")
        assert exito is False
        assert "Acceso denegado" in mensaje

    def test_usuario_reservado_root(self, servicio_acceso: Any):
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("root", "cualquiera")
        assert exito is False
        assert "Acceso denegado" in mensaje

    def test_usuario_reservado_case_insensitive(self, servicio_acceso: Any):
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("Admin", "cualquiera")
        assert exito is False
        assert "Acceso denegado" in mensaje

    def test_contrasena_incorrecta(self, servicio_acceso: Any, db: Any):
        _insertar_usuario(db, "testuser", "testpass", "2026-01-01", "2030-01-01", "test-serial")
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("testuser", "wrongpass")
        assert exito is False
        assert "inválidas" in mensaje

    def test_usuario_valido(self, servicio_acceso: Any, db: Any):
        _insertar_usuario(db, "valido", "pass123", "2026-01-01", "2030-01-01", "serial-valido")
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("valido", "pass123")
        assert exito is True
        assert "exitosa" in mensaje
        assert datos is not None
        assert datos["usuario"] == "valido"
        assert datos["serial"] == "serial-valido"
        assert datos["fecha_inicio"] == "2026-01-01"
        assert datos["fecha_fin"] == "2030-01-01"
        assert isinstance(datos.get("dias_restantes"), int)

    def test_licencia_vencida(self, servicio_acceso: Any, db: Any):
        _insertar_usuario(db, "vencido", "passven", "2020-01-01", "2020-06-01", "serial-vencido")
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("vencido", "passven")
        assert exito is False
        assert "Licencia" in mensaje
        assert "vencida" in mensaje

    def test_usuario_inexistente(self, servicio_acceso: Any):
        exito, mensaje, datos = servicio_acceso.autenticar_usuario("noexiste", "nopass")
        assert exito is False
        assert "inválidas" in mensaje


class TestGuardarPreferenciasSesion:
    def test_guardar_recordar_true(self, servicio_acceso: Any, cfg: Any):
        servicio_acceso.guardar_preferencias_sesion("usuario1", "pass1", True)
        ruta = cfg.obtener_ruta_config()
        with open(ruta) as f:
            config = json.load(f)
        assert config["usuario"] == "usuario1"
        assert config["contrasena"] != "pass1"
        assert len(config["contrasena"]) > 0
        assert config["recordar"] is True

    def test_guardar_recordar_false(self, servicio_acceso: Any, cfg: Any):
        servicio_acceso.guardar_preferencias_sesion("usuario2", "pass2", False)
        ruta = cfg.obtener_ruta_config()
        with open(ruta) as f:
            config = json.load(f)
        assert config["usuario"] == ""
        assert config["contrasena"] == ""
        assert config["recordar"] is False


class TestCargarPreferenciasSesion:
    def test_sin_preferencias(self, servicio_acceso: Any):
        usuario, contrasena, recordar = servicio_acceso.cargar_preferencias_sesion()
        assert usuario == ""
        assert contrasena == ""
        assert recordar is False

    def test_cargar_recordar_true(self, servicio_acceso: Any, cfg: Any):
        ruta = cfg.obtener_ruta_config()
        with open(ruta, "w") as f:
            json.dump({"usuario": "cargado", "contrasena": cifrar("secreta"), "recordar": True}, f)
        usuario, contrasena, recordar = servicio_acceso.cargar_preferencias_sesion()
        assert usuario == "cargado"
        assert contrasena == "secreta"
        assert recordar is True

    def test_cargar_recordar_false(self, servicio_acceso: Any, cfg: Any):
        ruta = cfg.obtener_ruta_config()
        with open(ruta, "w") as f:
            json.dump({"usuario": "ignorado", "contrasena": "ignorado", "recordar": False}, f)
        usuario, contrasena, recordar = servicio_acceso.cargar_preferencias_sesion()
        assert usuario == ""
        assert contrasena == ""
        assert recordar is False


class TestVerificarAccesoDesarrollador:
    def test_credenciales_correctas(self, servicio_acceso: Any):
        assert servicio_acceso.verificar_acceso_desarrollador("innobertdev", "ingsoftware.99") is True

    def test_usuario_incorrecto(self, servicio_acceso: Any):
        assert servicio_acceso.verificar_acceso_desarrollador("otro", "ingsoftware.99") is False

    def test_contrasena_incorrecta(self, servicio_acceso: Any):
        assert servicio_acceso.verificar_acceso_desarrollador("innobertdev", "wrongpass") is False

    def test_ambos_incorrectos(self, servicio_acceso: Any):
        assert servicio_acceso.verificar_acceso_desarrollador("usuario", "contrasena") is False


class TestPuedeAccederARegistro:
    def test_dev_puede_acceder(self, servicio_acceso: Any):
        assert servicio_acceso.puede_acceder_a_registro("innobertdev", "ingsoftware.99") is True

    def test_no_dev_no_puede_acceder(self, servicio_acceso: Any):
        assert servicio_acceso.puede_acceder_a_registro("usuario", "contrasena") is False


class TestCrearUsuarioPrueba:
    def test_ya_existe(self, servicio_acceso: Any, db: Any):
        resultado = servicio_acceso.crear_usuario_prueba()
        assert resultado is True

    def test_crea_usuario(self, servicio_acceso: Any, db: Any):
        with db.conexion() as conn:
            conn.cursor().execute("DELETE FROM usuarios WHERE usuario = 'prueba'")
        resultado = servicio_acceso.crear_usuario_prueba()
        assert resultado is True
        from retail.nucleo.base_datos import buscar_usuario
        assert buscar_usuario("prueba", "prueba") is not None


def _insertar_usuario(
    db: Any, usuario: str, contrasena: str, fecha_inicio: str, fecha_fin: str, serial: str
) -> None:
    hash_pw = hashlib.sha256(contrasena.encode()).hexdigest()
    with db.conexion() as conn:
        conn.cursor().execute(
            "INSERT INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
            (usuario, hash_pw, fecha_inicio, fecha_fin, serial),
        )
