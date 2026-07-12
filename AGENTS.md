# Contexto del Proyecto — Innobert Retail

## Última sesión (11 Jul 2026)
Se completaron 7 hitos principales:

### 1. Refactorización base_datos ✅
- Monolito `base_datos.py` (1160 líneas) → paquete modular `base_datos/`
- Nomenclatura unificada a español (sin mezclar inglés)
- Eliminados alias de retrocompatibilidad

### 2. Single Instance ✅
- `inicio.py` con `adquirir_instancia_unica()` vía socket
- Puerto derivado de SHA-256 del path del script

### 3. Entry point ✅
- Función `main()` en `inicio.py` para `pip install`
- `pyproject.toml` ya funcional: `innobert-retail = "inicio:main"`

### 4. Seguridad (bcrypt) ✅
- `retail/nucleo/seguridad.py` con `hash_contrasena()` y `verificar_contrasena()`
- Migración automática SHA-256 → bcrypt en login exitoso
- Seed data actualizado a bcrypt

### 5. Tests 372/372 ✅
- Suite completa al 100% verde

### 6. CI/CD (ruff + mypy) ✅
- ruff: 164 errores → 0 limpio
- mypy: estricto en 22 módulos core, 0 errores
- CI pipeline: ruff check → mypy → pytest 372 tests

### 7. Consolidación rutas duplicadas ✅
- Eliminado `retail/nucleo/servicios/sesion/` (4 archivos legacy)
- Todos los imports apuntan a `retail/sesion/core/*`
- Tests 372/372, ruff 0, mypy 0

## En progreso
### 8. Internacionalización (i18n) 🔄
- ✅ Módulo `retail/traducciones/` con `_()` y `establecer_idioma()`
- ✅ Archivos `es.json` y `en.json` con ~180 traducciones
- ✅ Strings envueltas en: `sesion/core/*` (3 servicios), `sesion/acceso.py`, `sesion/registro.py`, `sesion/licencias.py`
- [ ] Envolver strings en `retail/vistas/*` (ventas.py, deudas.py, inventario.py, ganancias.py, contenedor.py)
- [ ] Configurar selector de idioma en la UI (menú de configuración)
- [ ] Tests para verificar cambio de idioma

## Próximos pasos pendientes
- [ ] Módulo de backup/restore de la BD
- [ ] Agregar `__main__.py` para instalación vía pip
- [ ] Verificar funcionamiento del entry point `innobert-retail`
