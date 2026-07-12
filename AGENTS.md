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

## ✅ Completado (12 Jul 2026)

### 8. `__main__.py` y empaquetado pip ✅
- `retail/__main__.py` creado — permite `python -m retail`
- `pyproject.toml` arreglado: `[tool.setuptools.packages.find]` + `py-modules = ["inicio"]`
- `pip install -e .`funciona, wheel se genera correctamente
- Entry point `innobert-retail` instalado como ejecutable

### 9. Módulo de backup/restore ✅
- `retail/nucleo/base_datos/backup.py` con: `crear_backup()`, `listar_backups()`, `restaurar_backup()`, `limpiar_backups()`
- 9 tests en `tests/test_backup.py`
- Backups con UUID para evitar colisiones de nombre
- Restaura usando `sqlite3.backup()` con rollback automático en caso de error

### 10. Validación final ✅
- **ruff**: 0 errores
- **mypy**: 0 errores en 23 archivos core
- **pytest**: 381/381 pruebas pasan (372 originales + 9 backup)
- **Wheel**: `innobert_retail-1.0.0-py3-none-any.whl` generado sin errores

### 11. Ejecutable PyInstaller ✅
- `dist/InnobertRetail.exe` — ejecutable standalone de 35 MB
- `--onefile`: no requiere Python ni dependencias instaladas
- Incluye: `img/` (25 iconos), `fotos/` (default.png), `icono.ico`, traducciones
- Entry point: `inicio.py` con detección de instancia única
- Compatible con `resource_path()` para rutas en modo frozen

## Estado actual
- Aplicación completamente funcional como ejecutable `.exe`
- También instalable vía `pip` (wheel o `pip install -e .`)
- Alternativas de distribución: ejecutable en `dist/`, wheel en `dist/` (generado con `pip wheel . --no-deps`), o publicar en PyPI
