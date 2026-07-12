from __future__ import annotations

import json
import os


class TestTraducciones:
    def test_idioma_por_defecto_es_espanol(self):
        from retail.traducciones import idioma_actual
        assert idioma_actual() == "es"

    def test_establecer_idioma_en_cambia_idioma(self):
        from retail.traducciones import establecer_idioma, idioma_actual, _
        establecer_idioma("en")
        assert idioma_actual() == "en"
        establecer_idioma("es")

    def test_traduccion_en_encuentra_clave_existente(self):
        from retail.traducciones import establecer_idioma, _
        establecer_idioma("en")
        assert _("Ventas") == "Sales"
        assert _("Error") == "Error"
        assert _("Guardar") == "Save"
        establecer_idioma("es")

    def test_traduccion_en_fallback_si_no_existe(self):
        from retail.traducciones import establecer_idioma, _
        establecer_idioma("en")
        assert _("ClaveQueNoExiste123") == "ClaveQueNoExiste123"
        establecer_idioma("es")

    def test_traduccion_es_siempre_devuelve_original(self):
        from retail.traducciones import establecer_idioma, _
        establecer_idioma("es")
        assert _("Ventas") == "Ventas"
        assert _("Error") == "Error"

    def test_traduccion_con_formato(self):
        from retail.traducciones import establecer_idioma, _
        establecer_idioma("en")
        resultado = _("Bienvenido, {0}!").format("Admin")
        assert resultado == "Welcome, Admin!"
        establecer_idioma("es")

    def test_idioma_invalido_carga_vacio_y_fallback(self):
        from retail.traducciones import establecer_idioma, _
        establecer_idioma("xx")
        assert _("Ventas") == "Ventas"
        establecer_idioma("es")

    def test_en_json_tiene_todas_las_claves_necesarias(self):
        ruta = os.path.join(os.path.dirname(__file__), "..", "retail", "traducciones", "en.json")
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
        claves_requeridas = [
            "Ventas", "Deudas", "Inventario", "Clientes", "Ganancias",
            "INICIO DE SESIÓN", "Usuario", "Contraseña",
            "Iniciar Sesión", "Registrar", "Guardar", "Cancelar",
            "Error", "Éxito", "Advertencia", "Confirmar",
        ]
        for clave in claves_requeridas:
            assert clave in data, f"Falta traducción para: {clave}"
