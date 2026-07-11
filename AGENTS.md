# Contexto del Proyecto — Innobert Retail

## Última sesión (11 Jul 2026)
Se completaron 5 hitos principales:

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

## Próximos pasos pendientes
- [ ] Mejorar CI/CD (agregar mypy, ruff linting)
- [ ] Consolidar rutas duplicadas: `retail/nucleo/servicios/sesion/` y `retail/sesion/core/`
- [ ] Módulo de backup/restore de la BD
- [ ] Internacionalización (i18n)
- [ ] Agregar `__main__.py` para instalación vía pip
- [ ] Verificar funcionamiento del entry point `innobert-retail`
