# ✅ Checklist de presentación en GitHub

## Antes de hacer Push

- [ ] README.md está completo y bien estructurado
- [ ] Todas las secciones están debidamente indentadas
- [ ] Los enlaces funcionan correctamente
- [ ] No hay referencias a archivos que no existen
- [ ] Las rutas de imágenes son relativas (ej: `docs/gifs/archivo.gif`)
- [ ] Los badges están actualizados
- [ ] La tabla de contenidos está sincronizada

## Estructura recomendada de carpetas

```
project-root/
├── README.md              ← Archivo principal
├── LICENSE
├── .gitignore
├── docs/
│   ├── gifs/             ← GIFs demostrativos
│   ├── img/              ← Imágenes de documentación
│   └── GIFS_HOWTO.md     ← Guía para agregar GIFs
└── src/                  ← Código fuente
```

## Mejores prácticas para README en GitHub

### 1. Estructura clara
- Usa encabezados jerárquicos (#, ##, ###)
- Mantén las líneas bajo 100 caracteres
- Usa listas para información de fácil lectura

### 2. Emojis y formateo
- ✅ Usa emojis de forma consistente
- ✅ Destaca palabras clave con **negrita**
- ✅ Usa `monospace` para código
- ✅ Usa tablas para comparaciones

### 3. Enlaces
- Verifica que todos los enlaces funcionen
- Usa rutas relativas para archivos locales
- Usa URLs absolutas para sitios externos

### 4. Secciones recomendadas
1. Título con badges
2. Descripción breve
3. Características
4. Tabla de contenidos
5. Requisitos previos
6. Instalación
7. Uso
8. Estructura del proyecto
9. Tecnologías
10. Desarrollo/Contribución
11. Licencia
12. Contacto

## Validar README localmente

### Opción 1: Usar grip (gem install grip)
```bash
grip README.md
```

### Opción 2: Usar el preview de GitHub Desktop
- Abre GitHub Desktop
- Haz clic en "Preview" para ver cómo se verá

### Opción 3: Commitear a rama temporal
```bash
git checkout -b readme-preview
git add README.md
git commit -m "Preview README"
git push origin readme-preview
```

## Información sobre rutas de imágenes

### ✅ Rutas correctas
```markdown
![Alt text](docs/gifs/archivo.gif)
![Alt text](docs/img/imagen.png)
![Alt text](../docs/gifs/archivo.gif)
```

### ❌ Rutas incorrectas
```markdown
![Alt text](file:///C:/path/to/docs/gifs/archivo.gif)
![Alt text](\docs\gifs\archivo.gif)
![Alt text](docs\\gifs\\archivo.gif)
```

## Cómo resolver problemas comunes

### Las imágenes no se ven
- Verifica que la ruta sea relativa
- Confirma que el archivo existe en esa ruta
- Usa `/` no `\` en las rutas
- Codifica espacios en URLs: `Mi%20Archivo.png`

### Los enlaces no funcionan
- Verifica la sintaxis: `[text](url)`
- Confirma que el archivo existe
- Para enlaces internos, usa `#seccion` (minúsculas, sin espacios)

### El formateo se ve mal
- Agrega líneas en blanco entre secciones
- Usa `---` para separadores
- Verifica la indentación de listas

## Publicar a GitHub

### Primer envío
```bash
git add .
git commit -m "Actualizar README y estructura"
git push origin main
```

### Actualizaciones posteriores
```bash
git add README.md docs/
git commit -m "Actualizar documentación"
git push
```

---

**Última revisión:** Mayo 2026
