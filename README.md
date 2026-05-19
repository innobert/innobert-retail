# 🧾 Innobert Retail

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2011-0078D6?logo=windows&logoColor=white)]()
[![Linux](https://img.shields.io/badge/Linux-Debian%20%7C%20Ubuntu-FCC624?logo=linux&logoColor=black)]()

**Sistema de punto de venta profesional para pequeños comercios con control de deudas, inventario, facturación y análisis de ganancias.**

> 💡 *Ideal para tiendas de barrio, minimarkets y emprendedores que quieren dejar el cuaderno y lápiz atrás.*

---

## 🚀 Características principales

| Módulo | Descripción |
|--------|-------------|
| 🛒 **Ventas** | Carrito dinámico, cálculo automático de vuelto, facturación PDF, edición de transacciones |
| 💸 **Deudas** | Créditos con abonos parciales, historial completo, reporte de saldos pendientes |
| 📦 **Inventario** | CRUD completo de productos, soporte de imágenes (PNG, JPG, WEBP, GIF, BMP, TIFF, ICO), control de stock, historial |
| 👥 **Clientes** | Registro rápido, gestión directa en tabla, autocompletado inteligente |
| 📈 **Ganancias** | Reportes diario, semanal, mensual y anual desde la primera transacción |
| 🔐 **Seguridad** | Autenticación con suscripción de 30 días, contraseñas hasheadas (SHA-256) |
| 🗑️ **Papelera** | Recuperación de registros eliminados, limpieza automática de datos antiguos (>30 días) |
| 🎨 **Personalización** | Cambio de logo por transacción, múltiples formatos de imagen soportados |

---

## 📋 Tabla de contenidos

- [Requisitos previos](#-requisitos-previos)
- [Instalación rápida](#-instalación-rápida)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Cómo usar](#-cómo-usar)
- [Tecnologías](#-tecnologías)
- [Desarrollo](#-desarrollo)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## � Requisitos previos

- **Python 3.11 o superior** (con Tkinter incluido)
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)
- **Sistemas operativos soportados:**
  - Windows 10/11
  - Linux (Debian, Ubuntu, Fedora)
  - macOS (con soporte experimental)

---

## ⚡ Instalación rápida

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/innobert/innobert-retail.git
cd innobert-retail
```

### Paso 2: Crear entorno virtual

```bash
python -m venv venv
```

### Paso 3: Activar el entorno virtual

**En Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**En Windows (CMD):**
```batch
venv\Scripts\activate.bat
```

**En Linux/macOS:**
```bash
source venv/bin/activate
```

### Paso 4: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 5: Ejecutar la aplicación

```bash
python inicio.py
```

### Credenciales de prueba
- **Usuario:** `prueba`
- **Contraseña:** `prueba`

✅ La base de datos se crea automáticamente en:
- Windows: `%APPDATA%\InnobertRetail`
- Linux/macOS: `~/.local/share/innobert-retail`

---

## 📁 Estructura del proyecto

```
innobert-retail/
├── .git/                     # Repositorio Git
├── .gitignore                # Archivos ignorados
├── inicio.py                 # 🎯 Punto de entrada principal
├── requirements.txt          # Dependencias del proyecto
├── icono.ico                 # Ícono de la aplicación
├── LICENSE                   # Licencia MIT
├── README.md                 # Este archivo
│
├── img/                      # 🖼️ Recursos gráficos (iconos, login, etc.)
│   ├── login.png
│   ├── software.png
│   ├── logo.png
│   └── ... (más iconos)
│
├── fotos/                    # 📸 Imágenes de productos
│   └── default.png           # Imagen por defecto
│
├── docs/                     # 📚 Documentación
│   ├── gifs/                 # GIFs demostrativos
│   └── img/                  # Imágenes de documentación
│
└── retail/                   # 💼 Código fuente principal
    ├── inicio.py
    ├── vistas/               # 🎨 Interfaces gráficas
    │   ├── acceso.py         # Login y registro
    │   ├── contenedor.py     # Ventana principal
    │   ├── inventario.py     # Módulo de inventario
    │   ├── ventas.py         # Módulo de ventas
    │   ├── deudas.py         # Módulo de deudas
    │   └── clientes.py       # Módulo de clientes
    │
    ├── nucleo/               # ⚙️ Lógica de negocio
    │   ├── base_datos.py     # Operaciones SQLite
    │   ├── configuraciones.py# Rutas y configuración
    │   ├── principal.py      # Ventana principal
    │   └── servicios/        # Servicios por módulo
    │       ├── inventario/
    │       ├── ventas/
    │       ├── deudas/
    │       └── clientes/
    │
    ├── utilidades/           # 🔧 Funciones auxiliares
    │   └── logo.py          # Gestor de logo
    │
    ├── sesion/              # 🔐 Autenticación
    │   ├── login.py
    │   └── usuarios.py
    │
    ├── ganancias/           # 📊 Reportes
    │   ├── diario.py
    │   ├── semanal.py
    │   ├── mensual.py
    │   └── anual.py
    │
    └── inventario/          # 📦 Gestión de inventario
        └── historial_inventario.py
```

---

## 🎯 Cómo usar

### 📦 Módulo Inventario

1. Abre el módulo desde el menú principal
2. Haz clic en **Agregar** para crear un nuevo producto
3. Completa los campos:
   - **Nombre del producto**
   - **Precio de venta**
   - **Costo unitario**
   - **Stock disponible**
   - **Imagen** (PNG, JPG, WEBP, GIF, BMP, TIFF, ICO)
4. Guarda y el producto aparecerá en el canvas

### 🛒 Módulo Ventas

1. Selecciona cliente y producto
2. Agrega cantidad al carrito
3. Calcula automáticamente subtotales
4. Ingresa monto recibido
5. Genera factura PDF

### 💸 Módulo Deudas

1. Registra ventas con opción de crédito
2. Realiza abonos parciales
3. Consulta saldos pendientes
4. Descarga reporte de deudores

### 📈 Reportes de Ganancias

- **Diario:** Ganancias del día actual
- **Semanal:** Ganancias de los últimos 7 días
- **Mensual:** Ganancias del mes actual
- **Anual:** Ganancias del año actual

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Propósito | Versión |
|------------|-----------|---------|
| **Python** | Lenguaje principal | 3.11+ |
| **Tkinter** | Interfaz gráfica nativa | Incluido |
| **SQLite3** | Base de datos embebida | Incluido |
| **Pillow** | Procesamiento de imágenes | 12.2.0 |
| **ReportLab** | Generación de PDFs | Última |
| **PyInstaller** | Empaquetado ejecutable | Última |

---

## 👨‍💻 Desarrollo

### Clonar el repositorio

```bash
git clone https://github.com/innobert/innobert-retail.git
cd innobert-retail
```

### Instalar en modo desarrollo

```bash
python -m venv venv
# Activar venv (como se indicó arriba)
pip install -r requirements.txt
```

### Ejecutar con debugging

```bash
python -m pdb inicio.py
```

### Generar requirements.txt actualizado

```bash
pip freeze > requirements.txt
```

### Crear ejecutable para Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icono.ico inicio.py
```

El ejecutable estará en `dist/inicio.exe`

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Sigue estos pasos:

1. **Fork** el proyecto
2. Crea una rama para tu funcionalidad:
   ```bash
   git checkout -b feature/mi-funcionalidad
   ```
3. Realiza tus cambios y commitea:
   ```bash
   git commit -m "Agregar mi funcionalidad"
   ```
4. Sube la rama:
   ```bash
   git push origin feature/mi-funcionalidad
   ```
5. Abre un **Pull Request** describiendo los cambios

### Estándares de código

- Usa **Black** para formatear:
  ```bash
  pip install black
  black .
  ```
- Mantén funciones pequeñas y documentadas
- Comenta lógica compleja

---

## 📝 Licencia

Este proyecto se distribuye bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto

**Roberto Vásquez** (InnobertDev)

- 📞 WhatsApp: [+57 304 210 4313](https://wa.me/573042104313)
- 📷 Instagram: [@innobertdev](https://instagram.com/innobertdev)
- 📧 Email: [innobert07@gmail.com](mailto:innobert07@gmail.com)
- 🐙 GitHub: [innobert](https://github.com/innobert)

---

## ⭐ Agradecimiento

Si este software te ha sido útil en tu negocio, ¡no olvides darle una **estrella en GitHub**! ⭐

Tu apoyo es muy importante y nos motiva a seguir mejorando el proyecto.

---

## 🐛 Reportar problemas

Si encuentras un bug o deseas sugerir una mejora, abre un [Issue](https://github.com/innobert/innobert-retail/issues) describiendo:
- El problema o sugerencia
- Pasos para reproducirlo (si aplica)
- Capturas de pantalla si es necesario
- Tu versión de Python y SO

---

**Última actualización:** Mayo 2026 | **Versión:** 1.0.0