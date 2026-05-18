<!-- markdownlint-disable MD033 -->
# 🧾 Innobert Retail

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2011-0078D6?logo=windows&logoColor=white)]()
[![Linux](https://img.shields.io/badge/Linux-Debian%20%7C%20Ubuntu-FCC624?logo=linux&logoColor=black)]()

**Sistema de punto de venta, control de deudas, inventario, facturación y análisis de ganancias para pequeños comercios.**  
> 💡 *Ideal para tiendas de barrio, minimarkets y emprendedores que quieren dejar el cuaderno y lápiz.*

---

## 🚀 Características principales

| Módulo          | Funcionalidades clave                                                                                   |
|----------------|----------------------------------------------------------------------------------------------------------|
| 🛒 **Ventas**    | Carrito por cliente, monto recibido con vuelto automático, factura PDF, edición de facturas.             |
| 💸 **Deudas**    | Créditos con abonos parciales, historial completo, reporte de saldos pendientes.                        |
| 📦 **Inventario**| CRUD con imágenes, control de stock, historial de movimientos, totales de valor y ganancia potencial.   |
| 👥 **Clientes**  | Registro rápido, edición directa en tabla, búsqueda por autocompletado.                                 |
| 📈 **Ganancias** | Reportes diario, semanal, mensual y anual (períodos consecutivos desde la primera transacción).          |
| 🔐 **Seguridad** | Usuarios con suscripción de 30 días (renovable), contraseñas hasheadas (SHA‑256).                       |
| 🗑️ **Papelera**  | Recuperación de registros eliminados y limpieza automática de datos antiguos (>30 días).                |

---

## 🎥 Demostración interactiva (pendiente de añadir GIFs)

> 📸 *Puedes grabar GIFs de tu pantalla con herramientas como [ScreenToGif](https://www.screentogif.com/) (Windows) o [Peek](https://github.com/phw/peek) (Linux). Luego coloca los archivos en `docs/gifs/` y enlázalos aquí.*

<details>
<summary>▶️ Ver ejemplos (clic para expandir)</summary>

- **Agregar producto**  
  ![Agregar producto](docs/gifs/agregar_producto.gif)

- **Realizar venta**  
  ![Venta](docs/gifs/venta.gif)

- **Crear deuda y abonar**  
  ![Deuda](docs/gifs/deuda.gif)

</details>

---

## 📁 Estructura del proyecto (vista rápida)

```text
innobert-retail/
├── .gitignore          # Archivos ignorados (venv, __pycache__, etc.)
├── inicio.py           # Punto de entrada principal
├── requirements.txt    # Dependencias (pillow, reportlab)
├── img/                # Iconos y recursos gráficos (.png)
├── fotos/              # Imágenes de productos (default.png incluida)
├── retail/             # Código fuente principal
│   ├── deudas/         # Vistas y lógica de deudas
│   ├── ganancias/      # Reportes diario, semanal, mensual, anual
│   ├── inventario/     # CRUD de productos, historial, totales
│   ├── nucleo/         # Capa de datos y servicios
│   │   ├── base_datos.py        # Funciones SQLite
│   │   ├── configuraciones.py   # Rutas multiplataforma
│   │   ├── principal.py         # Ventana principal (Tk)
│   │   └── servicios/          # Lógica de negocio por módulo
│   ├── utilidades/      # Funciones auxiliares (cambiar logo)
│   ├── ventas/          # Vistas y lógica de ventas
│   ├── vistas/          # Frames principales (login, contenedor, etc.)
│   └── sesion/          # Autenticación y gestión de usuarios
├── README.md
└── LICENSE
```

> ⚠️ **Importante**: El directorio `venv/`, `__pycache__/`, `*.pyc` y la base de datos `pos.db` **no se incluyen en el repositorio** (están en `.gitignore`).

---

## 💻 Requisitos previos

- **Python 3.11 o superior** (incluye Tkinter)
- **pip** (gestor de paquetes)
- **Git** (opcional, para clonar)
- **Windows 10/11** o **Linux** (Debian/Ubuntu)

---

## ⚙️ Instalación y ejecución paso a paso

### 1. Clonar o descargar el repositorio

```bash
git clone https://github.com/innobert/innobert-retail.git
cd innobert-retail
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

**Windows (PowerShell)**

```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD)**

```batch
venv\Scripts\activate.bat
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar la aplicación

```bash
python inicio.py
```

### 6. Credenciales de prueba

- Usuario: `prueba`
- Contraseña: `prueba`

🔐 La primera ejecución creará la base de datos en `%APPDATA%\InnobertRetail` (Windows) o `~/.local/share/innobert-retail` (Linux).

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Propósito |
|------------|-----------|
| Python 3.11 | Lenguaje principal |
| Tkinter | Interfaz gráfica nativa |
| SQLite3 | Base de datos embebida (offline) |
| Pillow | Procesamiento de imágenes |
| ReportLab | Generación de PDFs (facturas, reportes) |
| PyInstaller | Empaquetado en ejecutable |

---

## 🧪 Desarrollo y contribuciones

1. Abre el proyecto en VS Code.
2. Selecciona el entorno virtual como intérprete (`Ctrl+Shift+P` → `Python: Select Interpreter` → `./venv/Scripts/python.exe`).
3. Instala extensiones recomendadas: Python, Pylance, Black Formatter.

### Comandos útiles

Formatear código automáticamente con Black:

```bash
black .
```

Generar `requirements.txt`:

```bash
pip freeze > requirements.txt
```

Crear ejecutable con PyInstaller (Windows):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icono.ico inicio.py
```

### ¿Cómo contribuir?

1. Haz un fork del proyecto.
2. Crea una rama para tu funcionalidad:

```bash
git checkout -b feature/nueva-funcionalidad
```

3. Realiza tus cambios y commitea:

```bash
git commit -m "Añadir nueva funcionalidad"
```

4. Sube la rama:

```bash
git push origin feature/nueva-funcionalidad
```

5. Abre un Pull Request describiendo los cambios.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.

---

## 📧 Contacto

- Roberto Vásquez (InnobertDev)
- WhatsApp: `+57 304 210 4313`
- Instagram: `@innobertdev`
- Email: `innobert07@gmail.com`

⭐ Si este software te ha sido útil, ¡no olvides darle una estrella en GitHub!

Simplemente copia todo el bloque de código de arriba y pégalo en tu archivo `README.md`. Asegúrate de que la extensión del archivo sea `.md` y que esté en la raíz de tu proyecto. ¡Listo para subir a GitHub!