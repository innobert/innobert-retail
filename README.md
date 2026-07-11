# Innobert Retail

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/licencia-Custom-red)](LICENSE.md)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows&logoColor=white)]()
[![Linux](https://img.shields.io/badge/Linux-Debian%20%7C%20Ubuntu-FCC624?logo=linux&logoColor=black)]()
[![macOS](https://img.shields.io/badge/macOS-experimental-999999?logo=apple&logoColor=white)]()
[![Tests](https://img.shields.io/badge/tests-250%2B-passing-green?logo=pytest)]()
[![Lines](https://img.shields.io/badge/code-21.800%2B%20lines-blue)]()
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
- [Agente por Voz](#agente-por-voz)
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

---

## Arquitectura

Arquitectura de 3 capas (MVC-like):

```
inicio.py  (punto de entrada + instancia única via socket)
    │
    └── retail/
        ├── nucleo/               ← Modelo (datos + servicios)
        │   ├── base_datos.py          (SQLite CRUD completo)
        │   ├── configuraciones.py     (paths, logging, tema)
        │   ├── principal.py           (Ventana Tk root)
        │   └── servicios/             ← Lógica de negocio
        │       ├── clientes/    ─── CRUD + validaciones
        │       ├── deudas/      ─── Créditos, pagos, edición
        │       ├── ganancias/   ─── Reportes diario/semanal/mensual/anual
        │       ├── inventario/  ─── CRUD + rentabilidad
        │       ├── sesion/      ─── Re-exports → auth core
        │       └── ventas/      ─── Carrito, edición, facturas
        │
        ├── vistas/               ← Vistas principales (tabs)
        ├── ventas/               ← Sub-vistas UI de ventas
        ├── deudas/               ← Sub-vistas UI de deudas
        ├── ganancias/            ← Sub-vistas UI de ganancias
        ├── inventario/           ← Sub-vistas UI de inventario
        ├── sesion/               ← Auth + licencias + registro
        └── utilidades/           ← Gestión de logo
```

- **Base de datos**: SQLite3 en `%APPDATA%/InnobertRetail/pos.db`
- **15 tablas**: usuarios, clientes, inventario, ventas, deudas, pagos, ganancias, historiales, papeleras
- **~250 pruebas** unitarias con pytest y base de datos en memoria
- **~62 archivos Python**, ~21,800 líneas de código

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
| **ReportLab 4.5.1** | Generación de PDFs |
| **Pillow 12.2.0** | Procesamiento de imágenes |
| **pytest** | Pruebas unitarias |
| **mypy** | Tipado estático (strict) |
| **requests** | Validación de licencias |

---

## Desarrollo

### Pruebas

```bash
# Todas las pruebas
pytest -v

# Con cobertura
pytest --cov=retail -v

# Módulo específico
pytest tests/test_base_datos.py -v
```

### Tipado

```bash
mypy retail/ --strict
```

### Empaquetado (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icono.ico inicio.py
```

El ejecutable se genera en `dist/inicio.exe`.

### Estructura de Archivos

```
retail/
├── nucleo/base_datos.py       # 1,335 lines — CRUD SQLite
├── nucleo/configuraciones.py  # 308 lines — paths, logging, tema
├── nucleo/principal.py        # 68 lines — ventana Tk root
├── nucleo/servicios/          # 22 archivos — lógica de negocio
├── vistas/                    # 6 archivos — vistas principales
├── ventas/                    # 6 archivos — sub-vistas ventas
├── deudas/                    # 7 archivos — sub-vistas deudas
├── ganancias/                 # 4 archivos — reportes
├── inventario/                # 2 archivos — historial, totales
├── sesion/                    # 5 archivos — auth, licencias
└── utilidades/                # 1 archivo — gestor de logo
```

---

## Agente por Voz

El proyecto incluye un módulo de reconocimiento de voz (`retail/agente/`) que permite ejecutar acciones mediante comandos hablados.

### Motor Recomendado: Vosk

- **Peso**: ~50MB el modelo en español
- **Latencia**: <1s en CPU
- **Offline**: 100% local, sin internet
- **Dependencias**: `vosk` (usa API nativa winmm de Windows)

### Instalación del modelo

```bash
pip install vosk
```

1. Descarga el modelo pequeño en español desde https://alphacephei.com/vosk/models
2. Extrae `vosk-model-small-es-0.42` en `retail/agente/modelos/`

### Comandos disponibles

| Comando | Acción |
|---------|--------|
| "ventas", "ir a ventas" | Abre módulo Ventas |
| "deudas", "ir a deudas" | Abre módulo Deudas |
| "inventario", "ver inventario" | Abre módulo Inventario |
| "clientes", "ver clientes" | Abre módulo Clientes |
| "facturas", "ver facturas" | Abre facturas de ventas |
| "facturas deudas" | Abre facturas de deudas |
| "carrito", "abrir carrito" | Abre carrito de ventas |
| "ganancias", "ver ganancias" | Abre reportes de ganancias |
| "papelera ventas" | Abre papelera de ventas |
| "ayuda", "comandos" | Muestra lista completa de comandos |
| "silenciar", "desactivar" | Desactiva el agente |
| "activar", "encender" | Reactiva el agente |

El botón **🎤 Voz** en el menú superior permite activar/desactivar el agente.

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
