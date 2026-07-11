# Innobert Retail

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/licencia-Custom-red)](LICENSE.md)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows&logoColor=white)]()
[![Linux](https://img.shields.io/badge/Linux-Debian%20%7C%20Ubuntu-FCC624?logo=linux&logoColor=black)]()
[![macOS](https://img.shields.io/badge/macOS-experimental-999999?logo=apple&logoColor=white)]()
[![Tests](https://img.shields.io/badge/tests-372%20passed-green?logo=pytest)]()
[![Lines](https://img.shields.io/badge/code-22.500%2B%20lines-blue)]()
[![SQLite](https://img.shields.io/badge/database-SQLite-07405E?logo=sqlite&logoColor=white)]()
[![ReportLab](https://img.shields.io/badge/PDF-ReportLab-red)]()

**Sistema POS profesional para pequeños comercios** — Control de ventas, deudas, inventario, clientes y análisis de ganancias con interfaz gráfica nativa.

> Diseñado para tiendas de barrio, minimarkets, licorerías y emprendedores en Latinoamérica.

---

## Tabla de Contenidos

- [Capturas](#capturas)
- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Módulos](#módulos)
- [Tecnologías](#tecnologías)
- [Desarrollo](#desarrollo)
- [Licencia](#licencia)
- [Contacto](#contacto)

---

## Capturas

| Login | Ventas | Inventario |
|-------|--------|------------|
| ![Login](img/login.png) | ![Ventas](docs/gifs/ventas_pagar.gif) | ![Inventario](docs/gifs/inventario_agregar_producto.gif) |

| Deudas | Ganancias | Clientes |
|--------|-----------|----------|
| ![Deudas](docs/gifs/deudas_registrar.gif) | ![Ganancias](docs/gifs/ganancias.gif) | ![Clientes](docs/gifs/clientes_agregar.gif) |

---

## Características

### Módulos Principales

| Módulo | Descripción |
|--------|-------------|
| **Ventas** | Carrito dinámico, cálculo automático de vuelto, facturación PDF, edición de transacciones, historial completo |
| **Deudas/Crédito** | Créditos con abonos parciales, pagos con vuelto, historial por cliente, saldos, papelera |
| **Inventario** | CRUD completo, soporte de imágenes (PNG, JPG, WEBP, GIF, BMP, TIFF, ICO), control de stock, historial de movimientos, rentabilidad |
| **Clientes** | Registro, edición inline en tabla, autocompletado, validación de cédula/celular único |
| **Ganancias** | Reportes diario, semanal, mensual y anual con exportación PDF |
| **Papelera** | Recuperación de registros eliminados, limpieza automática > 30 días |
| **Personalización** | Logo personalizado para facturas PDF, imágenes de productos |

### Funcionalidades Clave

- **Instancia única**: Previene ejecución múltiple mediante socket localhost
- **Auditoría completa**: Cada transacción registra fecha, hora, usuario y detalle
- **Licenciamiento incorporado**: Sistema de trial de 30 días con SHA-256 y seriales UUID
- **Backdoor de desarrollo**: Acceso admin con credenciales de respaldo
- **Multiplataforma**: Windows, Linux y macOS (experimental)
- **PDF profesional**: Facturas con logo, productos detallados y totales via ReportLab
- **Carga asíncrona**: Datos de ganancias sin congelar la UI con threading
- **Variables de entorno**: `RETAIL_DATA_DIR`, `RETAIL_DB_NAME`, `RETAIL_LOG_LEVEL`, `RETAIL_LOG_DIR`
- **Encriptación de config**: Contraseñas cifradas en `config.json` vía Fernet (fallback XOR puro Python)
- **Paletas de color por módulo**: Botones estandarizados con colores diferenciados para ventas (azul) y deudas (rojo)

---

## Arquitectura

Arquitectura de 3 capas (MVC-like) con capa de servicios intermedia:

```
inicio.py  (punto de entrada + instancia única via socket)
    │
    └── retail/
        ├── nucleo/                           ← Modelo (datos + servicios)
        │   ├── base_datos/                   ← Paquete de acceso a datos (13 archivos)
        │   │   ├── conexion.py               ─── Conexión SQLite (context manager + directa)
        │   │   ├── _config_db.py             ─── Configuración de ruta de BD
        │   │   ├── esquema.py                ─── Creación de tablas
        │   │   ├── clientes.py               ─── CRUD clientes
        │   │   ├── inventario.py             ─── CRUD productos
        │   │   ├── ventas.py                 ─── Ventas + detalle_venta
        │   │   ├── deudas.py                 ─── Deudas + detalle_deuda + pagos
        │   │   ├── ganancias.py              ─── Totales por periodo
        │   │   ├── historiales.py            ─── Auditoría
        │   │   ├── papelera.py               ─── Soft delete
        │   │   ├── usuarios.py               ─── CRUD usuarios
        │   │   ├── indices.py                ─── Constantes de índice
        │   │   └── formateo.py               ─── Formato moneda
        │   │
        │   ├── configuraciones.py            ← Paths, logging, tema UI, .env, cifrado
        │   ├── cifrado.py                    ← Encriptación Fernet + fallback XOR
        │   ├── principal.py                  ← Ventana Tk root
        │   └── servicios/                    ← Lógica de negocio (24 archivos)
        │       ├── base/                     ─── Clases base (transacción, carrito, papelera)
        │       ├── clientes/servicio_clientes.py
        │       ├── deudas/                   ─── 7 servicios (deudas, carrito, edición,
        │       │                                facturas, historial, pagadas, papelera, visualizar)
        │       ├── ganancias/                ─── 4 servicios (diario, semanal, mensual, anual)
        │       ├── inventario/servicio_inventario.py
        │       ├── sesion/                   ─── Re-exports de auth
        │       └── ventas/                   ─── 7 servicios (ventas, carrito, edición,
        │                                     facturas, historial, papelera, visualizar)
        │
        ├── vistas/               ← 6 vistas principales (tabs del contenedor)
        ├── ventas/               ← 6 sub-vistas UI de ventas
        ├── deudas/               ← 7 sub-vistas UI de deudas
        ├── ganancias/            ← 4 sub-vistas UI de ganancias
        ├── inventario/           ← 2 sub-vistas UI de inventario
        ├── sesion/               ← Auth + licencias + registro
        └── utilidades/           ← Gestión de logo
```

- **Base de datos**: SQLite3 en `%APPDATA%/InnobertRetail/pos.db`
- **15 tablas**: usuarios, clientes, inventario, ventas, deudas, pagos, ganancias, historiales, papeleras
- **372 pruebas** unitarias con pytest y base de datos en memoria
- **95 archivos Python**, ~22,500 líneas de código

---

## Requisitos

- **Python 3.11+** (con Tkinter incluido)
- **pip** (gestor de paquetes)
- **Sistemas operativos:**
  - Windows 10/11 (soporte nativo)
  - Linux (Debian, Ubuntu, Fedora)
  - macOS (experimental)

---

## Instalación

### 1. Clonar

```bash
git clone https://github.com/innobert/innobert-retail.git
cd innobert-retail
```

### 2. Entorno virtual

```bash
python -m venv venv
```

**Windows:**
```bash
source venv/Scripts/activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar

```bash
python inicio.py
```

### Credenciales de Prueba

| Usuario | Contraseña | Tipo |
|---------|-----------|------|
| `prueba` | `prueba` | Usuario trial 30 días |
| `innobertdev` | `ingsoftware.99` | Admin (backdoor) |

---

## Uso Rápido

### Flujo de Venta

1. Selecciona un producto del grid o escríbelo en el buscador
2. Define la cantidad
3. (Opcional) Selecciona cliente para venta por mayor
4. Abre el **Carrito** para revisar
5. Ingresa el monto recibido (el vuelto se calcula automáticamente)
6. Confirma → se genera la factura y el PDF

### Flujo de Deuda

1. Selecciona un **cliente** (obligatorio)
2. Agrega productos al carrito de deuda
3. Confirma → se registra el crédito
4. Para pagar: ve a Facturas → selecciona deuda → Pagar
5. Ingresa monto (abono o pago total)

### Gestión de Inventario

1. Botón **Agregar** → completa nombre, precio, costo, stock, imagen
2. Doble click en producto del grid para editar
3. Botón **Historial** para ver movimientos
4. Botón **Totales** para ver rentabilidad general

---

## Módulos

Cada módulo incluye documentación visual con GIFs en `docs/gifs/`:

### Inventario
- Agregar, editar, eliminar productos con imágenes
- Control de stock automático al vender
- Historial de movimientos por producto
- Filtro de búsqueda en tiempo real
- Totales de valor, costo y ganancia potencial

### Clientes
- Registro con validación de cédula y celular únicos
- Edición directa en tabla (doble click)
- Autocompletado inteligente
- Paginación (20 clientes/página)

### Ventas
- Carrito dinámico con validación de stock
- Cálculo automático de vuelto en tiempo real
- Ventas rápidas (sin cliente) y por mayor
- Facturación PDF con logo personalizado
- Edición de facturas existentes
- Historial completo de cambios

### Deudas
- Créditos con cliente obligatorio
- Abonos parciales con cálculo de vuelto
- Pagos totales que cierran la deuda automáticamente
- Historial por deuda y por cliente
- Deudas pagadas con reportes PDF

### Ganancias
- Reportes diario, semanal, mensual y anual
- Datos combinados: ventas + deudas pagadas
- Exportación a PDF por periodo
- Carga asíncrona sin congelar UI

---

## Tecnologías

| Tecnología | Propósito |
|------------|-----------|
| **Python 3.11+** | Lenguaje principal |
| **Tkinter (ttk "clam")** | Interfaz gráfica nativa |
| **SQLite3** | Base de datos embebida |
| **ReportLab** | Generación de PDFs |
| **Pillow** | Procesamiento de imágenes |
| **pytest + pytest-cov** | Pruebas unitarias y cobertura |
| **mypy** | Tipado estático (strict) |
| **cryptography** | Encriptación Fernet (con fallback XOR puro) |
| **requests** | Validación de licencias |
| **pyinstaller** | Empaquetado a ejecutable |

---

## Desarrollo

### Pruebas

```bash
# Todas las pruebas
pytest -v

# Con cobertura
pytest --cov=retail -v

# Módulo específico
pytest tests/test_servicio_ventas.py -v
```

### Tipado

```bash
mypy retail/ --strict
```

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `RETAIL_DATA_DIR` | Directorio de datos de usuario | `%APPDATA%/InnobertRetail` |
| `RETAIL_DB_NAME` | Nombre de la base de datos | `pos.db` |
| `RETAIL_LOG_LEVEL` | Nivel de logging | `DEBUG` |
| `RETAIL_LOG_DIR` | Directorio de logs | `{DATA_DIR}/logs` |

### Empaquetado (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icono.ico inicio.py
```

El ejecutable se genera en `dist/inicio.exe`.

---

## Licencia

Este proyecto se distribuye bajo una **Licencia Custom**. Consulta el archivo [LICENSE.md](LICENSE.md) para más detalles.

**Resumen**: Uso personal, estudio y local deployment permitidos. Prohibida la comercialización o redistribución sin autorización. Licencia trial de 30 días por defecto.

---

## Contacto

**Roberto Vásquez** (InnobertDev)

- WhatsApp: [+57 304 210 4313](https://wa.me/573042104313)
- Instagram: [@innobertdev](https://instagram.com/innobertdev)
- Email: [innobert07@gmail.com](mailto:innobert07@gmail.com)
- GitHub: [innobert](https://github.com/innobert)

---

## ⭐ ¿Te es útil?

Si este software te ha servido en tu negocio, **deja una estrella en GitHub**. Tu apoyo motiva a seguir mejorando.

---

*Última actualización: Julio 2026 | Versión: 1.0.0*
