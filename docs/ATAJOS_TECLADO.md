# Atajos de Teclado - Innobert Retail

## Navegación General

| Atajo | Acción | Descripción |
|-------|--------|-------------|
| `Ctrl+1` | Ir a Ventas | Cambia a la sección de Ventas |
| `Ctrl+2` | Ir a Deudas | Cambia a la sección de Deudas |
| `Ctrl+3` | Ir a Inventario | Cambia a la sección de Inventario |
| `Ctrl+4` | Ir a Clientes | Cambia a la sección de Clientes |
| `F1` | Ayuda | Muestra la ventana de ayuda con atajos |
| `Escape` | Cancelar | Cancela la acción actual |

---

## Atajos por Sección

### Clientes (`Ctrl+4`)

| Atajo | Acción | Descripción |
|-------|--------|-------------|
| `Ctrl+N` | Nuevo cliente | Limpia los campos para un nuevo registro |
| `Ctrl+G` | Guardar | Agrega el cliente con los datos ingresados |
| `Ctrl+B` | Buscar | Enfoca el campo de búsqueda |
| `Ctrl+E` | Editar | Edita el cliente seleccionado en la tabla |
| `Ctrl+L` | Limpiar | Limpia todos los campos del formulario |
| `Suprimir` | Eliminar | Elimina el cliente seleccionado |
| `Enter` | Confirmar | Siguiente campo o guardar (según contexto) |
| `↑↓` | Navegar | Navega entre clientes en la tabla |

### Ventas (`Ctrl+1`)

| Atajo | Acción | Descripción |
|-------|--------|-------------|
| `Ctrl+N` | Nueva venta | Inicia una nueva venta (limpia carrito) |
| `Ctrl+G` | Guardar | Procesa/guarda la venta actual |
| `Ctrl+B` | Buscar | Enfoca el campo de búsqueda de productos |
| `Ctrl+C` | Carrito | Abre la ventana del carrito |
| `Ctrl+L` | Limpiar | Limpia la búsqueda de productos |
| `Enter` | Confirmar | Selecciona producto o cliente (según contexto) |

### Deudas (`Ctrl+2`)

| Atajo | Acción | Descripción |
|-------|--------|-------------|
| `Ctrl+N` | Nueva deuda | Inicia una nueva deuda (limpia carrito) |
| `Ctrl+G` | Guardar | Procesa/guarda la deuda actual |
| `Ctrl+B` | Buscar | Enfoca el campo de búsqueda de productos |
| `Ctrl+C` | Carrito | Abre la ventana del carrito de deudas |
| `Ctrl+L` | Limpiar | Limpia la búsqueda de productos |
| `Enter` | Confirmar | Selecciona producto o cliente (según contexto) |

### Inventario (`Ctrl+3`)

| Atajo | Acción | Descripción |
|-------|--------|-------------|
| `Ctrl+N` | Nuevo producto | Limpia los campos para un nuevo producto |
| `Ctrl+G` | Guardar | Guarda el producto actual |
| `Ctrl+B` | Buscar | Enfoca el campo de búsqueda |
| `Ctrl+E` | Editar | Edita el producto seleccionado |
| `Ctrl+L` | Limpiar | Limpia la búsqueda de productos |
| `Suprimir` | Eliminar | Elimina el producto seleccionado |
| `Enter` | Confirmar | Selecciona producto (según contexto) |

---

## Comportamiento de la Tecla Enter

La tecla `Enter` funciona de manera independiente en cada interfaz:

### En Formularios (Clientes, Inventario)
- **Primer campo**: Avanza al siguiente campo
- **Último campo**: Guarda el registro
- **Campo con datos**: Avanza al siguiente campo vacío

### En Búsquedas (Combobox)
- **Ejecuta la búsqueda** con el texto actual
- **Selecciona el primer resultado** si hay coincidencia

### En Tablas
- **Selecciona el elemento** resaltado
- **Abre edición** si ya está seleccionado

### En Carrito (Ventas, Deudas)
- **Agrega producto** al carrito
- **Procesa venta/deuda** si el carrito tiene productos

---

## Notas Importantes

1. **Los atajos son independientes por ventana**: Cada ventana modal o popup tiene sus propios atajos
2. **No hay conflicto entre secciones**: Los atajos solo están activos en la sección visible
3. **Escape cancela**: En cualquier ventana modal, `Escape` cierra sin guardar
4. **Enter confirma**: En formularios, `Enter` avanza o guarda según el contexto

---

## Ejemplos de Uso Rápido

### Agregar Cliente Rápidamente
```
1. Ctrl+4 (ir a Clientes)
2. Ctrl+N (limpiar para nuevo)
3. Digitar nombre → Enter
4. Digitar apellidos → Enter
5. Digitar cédula → Enter
6. Digitar celular → Enter
7. Digitar zona → Enter (o Ctrl+G para guardar)
```

### Buscar y Editar Cliente
```
1. Ctrl+4 (ir a Clientes)
2. Ctrl+B (enfocar búsqueda)
3. Digitar nombre del cliente
4. Enter (ejecutar búsqueda)
5. ↑↓ (seleccionar cliente)
6. Ctrl+E (editar)
```

### Crear Venta Rápida
```
1. Ctrl+1 (ir a Ventas)
2. Digitar nombre producto → Enter (seleccionar)
3. Repetir para más productos
4. Ctrl+G (procesar venta)
```