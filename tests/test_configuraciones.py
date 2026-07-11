from __future__ import annotations

from pathlib import Path


class TestRutaDatosUsuario:
    def test_windows_devuelve_appdata(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")

        from retail.nucleo.configuraciones import _obtener_ruta_base_datos_usuario

        ruta = _obtener_ruta_base_datos_usuario()
        assert ruta == "C:\\Users\\Test\\AppData\\Roaming\\InnobertRetail"

    def test_linux_devuelve_xdg(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "linux")
        monkeypatch.setenv("XDG_DATA_HOME", "/home/test/.local/share")

        import importlib
        import retail.nucleo.configuraciones as cfg
        importlib.reload(cfg)

        ruta = cfg._obtener_ruta_base_datos_usuario()
        assert ruta.replace("\\", "/") == "/home/test/.local/share/InnobertRetail"


class TestFuncionesRuta:
    def test_obtener_ruta_base_datos(self, cfg):
        ruta = cfg.obtener_ruta_base_datos()
        assert ruta.endswith("pos.db")

    def test_obtener_ruta_config_dir(self, cfg):
        ruta = cfg.obtener_ruta_config_dir()
        assert ruta.endswith("config")

    def test_obtener_ruta_config(self, cfg):
        ruta = cfg.obtener_ruta_config()
        assert ruta.endswith("config.json")

    def test_obtener_ruta_pdf_config(self, cfg):
        ruta = cfg.obtener_ruta_pdf_config()
        assert ruta.endswith("pdf_config.json")

    def test_obtener_ruta_img_sin_argumento(self, cfg):
        ruta = cfg.obtener_ruta_img()
        assert ruta == cfg.FOTOS_PATH

    def test_obtener_ruta_img_con_nombre(self, cfg):
        ruta = cfg.obtener_ruta_img("producto.png")
        assert ruta.endswith("producto.png")

    def test_obtener_ruta_fotos_sin_argumento(self, cfg):
        ruta = cfg.obtener_ruta_fotos()
        assert ruta == cfg.FOTOS_PATH

    def test_obtener_ruta_fotos_con_nombre(self, cfg):
        ruta = cfg.obtener_ruta_fotos("foto.jpg")
        assert ruta.endswith("foto.jpg")

    def test_obtener_ruta_icon_sin_argumento(self, cfg):
        ruta = cfg.obtener_ruta_icon()
        assert ruta == cfg.APPDATA_PATH

    def test_obtener_ruta_icon_con_nombre(self, cfg):
        ruta = cfg.obtener_ruta_icon("icono.ico")
        assert ruta.endswith("icono.ico")

    def test_obtener_ruta_logo_sin_argumento(self, cfg):
        ruta = cfg.obtener_ruta_logo()
        assert ruta == cfg.LOGO_PATH

    def test_obtener_ruta_logo_con_nombre(self, cfg):
        ruta = cfg.obtener_ruta_logo("mi_logo.png")
        assert ruta.endswith("mi_logo.png")

    def test_obtener_ruta_carpeta_ventas(self, cfg):
        ruta = cfg.obtener_ruta_carpeta_ventas()
        assert ruta.endswith("Desktop\\ventas") or ruta.endswith("Desktop/ventas")

    def test_rutas(self, cfg):
        ruta = cfg.rutas("subcarpeta/archivo.txt")
        assert ruta.endswith("subcarpeta/archivo.txt") or ruta.endswith("subcarpeta\\archivo.txt")


class TestGuardarCargarUsuario:
    def test_guardar_y_cargar_usuario(self, cfg, tmp_appdata):
        cfg.guardar_usuario("admin", "1234", True)
        usuario, contrasena, recordar = cfg.cargar_usuario()
        assert usuario == "admin"
        assert contrasena == "1234"
        assert recordar is True

    def test_cargar_usuario_sin_recordar(self, cfg, tmp_appdata):
        cfg.guardar_usuario("user", "pass", False)
        usuario, contrasena, recordar = cfg.cargar_usuario()
        assert usuario == ""
        assert contrasena == ""
        assert recordar is False

    def test_cargar_usuario_sin_archivo(self, cfg):
        usuario, contrasena, recordar = cfg.cargar_usuario()
        assert usuario == ""
        assert contrasena == ""
        assert recordar is False


class TestPdfConfig:
    def test_guardar_y_cargar_ultima_carpeta(self, cfg, tmp_appdata, tmp_path):
        carpeta_test = str(tmp_path / "carpeta_ventas")
        Path(carpeta_test).mkdir(parents=True, exist_ok=True)
        cfg.guardar_ultima_carpeta_pdf("ventas", carpeta_test)
        carpeta = cfg.cargar_ultima_carpeta_pdf("ventas")
        assert carpeta == carpeta_test

    def test_cargar_carpeta_inexistente_devuelve_escritorio(self, cfg):
        carpeta = cfg.cargar_ultima_carpeta_pdf("deudas")
        assert "Desktop" in carpeta or "Escritorio" in carpeta

    def test_guardar_y_cargar_carpeta_inexistente(self, cfg, tmp_appdata):
        cfg.guardar_ultima_carpeta_pdf("ganancias", "Z:\\ruta_que_no_existe")
        carpeta = cfg.cargar_ultima_carpeta_pdf("ganancias")
        assert "Desktop" in carpeta


class TestAsegurarDirectorios:
    def test_asegurar_directorios_crea_carpetas(self, cfg, tmp_appdata):
        cfg.asegurar_directorios()
        assert Path(cfg.APPDATA_PATH).exists()
        assert Path(cfg.FOTOS_PATH).exists()
        assert Path(cfg.LOGO_PATH).exists()


class TestEliminarDatos:
    def test_eliminar_base_datos(self, cfg, tmp_appdata):
        db_path = Path(cfg.obtener_ruta_base_datos())
        db_path.write_text("fake db")
        assert db_path.exists()
        cfg.eliminar_base_datos()
        assert not db_path.exists()

    def test_eliminar_datos_completos(self, cfg, tmp_appdata):
        cfg.asegurar_directorios()
        assert Path(cfg.APPDATA_PATH).exists()
        resultado = cfg.eliminar_datos_completos()
        assert resultado is True
        assert not Path(cfg.APPDATA_PATH).exists()
