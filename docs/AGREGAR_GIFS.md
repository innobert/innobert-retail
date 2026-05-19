# 🎬 Cómo agregar GIFs para que se muestren en GitHub

## ✅ Lo que ya hicimos

Tu primer GIF **`inventario_agregar_producto.gif`** ya está en GitHub y se mostrará automáticamente en el README bajo la sección "1.1 Agregar Producto".

**URL en GitHub:** https://github.com/innobert/innobert-retail/blob/main/docs/gifs/inventario_agregar_producto.gif

---

## 🎯 Cómo agregar los próximos GIFs

### Paso 1: Grabar el GIF

Usa una herramienta como **ScreenToGif** (Windows) o **Peek** (Linux):

1. Abre ScreenToGif
2. Selecciona el área a grabar
3. Graba la acción (máximo 15 segundos)
4. Exporta como **GIF** (no MP4)

### Paso 2: Guardar con el nombre correcto

Guarda el archivo en: `docs/gifs/`

**Nombres exactos según lista:**
- `inventario_editar_producto.gif`
- `inventario_eliminar_producto.gif`
- `inventario_historial.gif`
- `inventario_buscar.gif`
- `clientes_agregar.gif`
- etc.

### Paso 3: Verifica que esté en la carpeta correcta

```
c:\Users\Win10\Desktop\retail\venv\
└── docs\
    └── gifs\
        ├── inventario_agregar_producto.gif  ✅ (ya existe)
        ├── inventario_editar_producto.gif   ← Aquí va el nuevo
        └── ...
```

### Paso 4: Commit y Push a GitHub

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
cd c:\Users\Win10\Desktop\retail\venv

# Agregar el nuevo GIF
git add docs/gifs/inventario_editar_producto.gif

# Commitear
git commit -m "Agregar GIF: editar producto en inventario"

# Enviar a GitHub
git push origin main
```

### Paso 5: Verifica en GitHub

1. Abre https://github.com/innobert/innobert-retail
2. Ve al README.md
3. Baja a la sección **1.2 Editar Producto**
4. Verás el GIF renderizado automáticamente ✅

---

## 📋 Proceso rápido (para repetir)

```powershell
# 1. Navega a la carpeta
cd c:\Users\Win10\Desktop\retail\venv

# 2. Agrega el archivo
git add docs/gifs/nombre_del_gif.gif

# 3. Commitea
git commit -m "Agregar GIF: descripcion"

# 4. Sube a GitHub
git push origin main
```

---

## ⚙️ Parámetros importantes para los GIFs

| Parámetro | Recomendación | Razón |
|-----------|----------------|-------|
| **Resolución** | Mínimo 1280x720 | Se ve nítido en GitHub |
| **Duración** | 6-15 segundos | No es muy largo |
| **Tamaño** | Máximo 10 MB | GitHub lo soporta bien |
| **FPS** | 10-15 FPS | Reproduce bien |
| **Nombre** | Sin espacios, con guion | `inventario_agregar.gif` |

---

## 🔍 Verificar que se ve bien

### En local (antes de subir)

1. Abre el navegador
2. Ve a `c:\Users\Win10\Desktop\retail\venv\README.md`
3. Usa una extensión de Markdown para ver cómo se verá

### En GitHub

1. Entra a: https://github.com/innobert/innobert-retail/
2. Verifica que el GIF aparezca en el README
3. Debería reproducirse automáticamente

---

## ❌ Problemas comunes

### El GIF no aparece en GitHub

**Posibles causas:**
- ❌ El archivo está en la carpeta incorrecta
- ❌ El nombre no coincide exactamente con el del README
- ❌ No hiciste `git push` correctamente
- ❌ El archivo es muy grande (>50 MB)

**Solución:**
1. Verifica la ruta: `docs/gifs/nombre_exacto.gif`
2. Verifica el README: el nombre debe coincidir 100%
3. Ejecuta: `git status` (verifica que todo esté committed)
4. Intenta nuevamente: `git push origin main`

### El GIF se ve borroso o pixelado

- Regrabalo con mayor resolución (mínimo 1280x720)
- Asegúrate de usar calidad alta en ScreenToGif

### El GIF es demasiado grande

- Reduce los FPS a 10-12
- Acorta la duración a máximo 12 segundos
- Usa ScreenToGif para "optimizar" antes de exportar

---

## 📋 Checklist antes de hacer commit

- [ ] El archivo está en `docs/gifs/`
- [ ] El nombre coincide exactamente con lo del README
- [ ] El GIF se reproduce correctamente (local)
- [ ] El tamaño es menor a 10 MB
- [ ] La resolución es mínimo 1280x720
- [ ] Ejecutaste `git add docs/gifs/archivo.gif`
- [ ] Ejecutaste `git commit -m "Mensaje descriptivo"`
- [ ] Ejecutaste `git push origin main`

---

## 🎬 Próximos GIFs por prioridad

Ve a `docs/GIFS_LIST.md` para ver la lista completa con prioridades.

---

**Tip:** Una vez que hayas agregado 2-3 GIFs más, el README lucirá mucho más profesional en GitHub. ¡Sigue adelante! 🚀
