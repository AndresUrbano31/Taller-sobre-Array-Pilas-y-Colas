# 📦 Amazon Hub — Simulador de Logística y Rutas de Entrega

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF9900?style=for-the-badge&logo=python&logoColor=white)
![Estructuras](https://img.shields.io/badge/Estructuras-Cola%20·%20Pila%20·%20Array-a371f7?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> Simulador educativo de un centro de distribución masivo que implementa **Colas (FIFO)**, **Pilas (LIFO)** y **Arrays bidimensionales** con interfaz gráfica interactiva en Tkinter.

---

## 🖼 Vista de la Interfaz

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📦 AMAZON HUB — Simulador de Logística          ● SISTEMA OPERATIVO   │
├──────────────────┬──────────────────────────────────┬───────────────────┤
│  📥 COLA FIFO    │  [ID] [Destino] [Tipo] +REGISTRAR│  🗂 INVENTARIO    │
│                  ├──────────────────────────────────┤  Array[cat][slot] │
│  1 PKG-001 ◀    │  ▶Cola  🚛Camión  ⬇LIFO  🚀Desp  │                   │
│  2 PKG-002       ├──────────────────────────────────┤  📁 Normal  1/5   │
│  3 PKG-003       │  📚 ESTANTERÍAS — Array[6][5]    │  📁 Frágil  1/5   │
│                  │  NOR FRÁ PES EXP DEV REF         │  📁 Pesado  1/5   │
│  ─────────────  │  [PKG][PKG][PKG][ ][ ][ ]        │  📁 Express 1/5   │
│  EN COLA    : 3  ├──────────────────────────────────┤                   │
│  CAMIÓN     : 1  │  🚛 CAMIÓN — Pila (LIFO)         │  🗺 RUTA ÓPTIMA   │
│  ENTREGADOS : 0  │  ► PKG-001  Zona Norte ←1º       │  1. Zona Norte    │
│  ESTANTES   : 4  ├──────────────────────────────────┤  2. Zona Sur      │
│                  │  ⬛ LOG: [10:32] Cola.encolar()   │  3. Zona Este     │
└──────────────────┴──────────────────────────────────┴───────────────────┘
```

---

## 📋 Contexto del Proyecto

Simular la gestión de un **centro de distribución masivo** donde los paquetes:

1. **Llegan** desde clientes en orden de llegada
2. **Se clasifican** por tipo y se almacenan en estanterías físicas
3. **Se cargan** en camiones optimizando la ruta de entrega
4. **Se despachan** siguiendo el orden LIFO para minimizar paradas

---

## ✅ Requerimientos Implementados

### 📥 Donde Usar Colas — `Queue (FIFO)`
> Recepción de pedidos de los clientes en orden de llegada.

- El primer paquete en llegar es el primero en ser procesado
- Garantiza equidad y orden en la atención de pedidos
- Implementado con `collections.deque` para operaciones O(1)

```python
cola = Cola()
cola.encolar(paquete)    # Cliente envía paquete → va al final de la fila
pkg  = cola.desencolar() # Se atiende el primero que llegó (FIFO)
```

---

### 🚛 Donde Usar Pilas — `Stack (LIFO)`
> Gestión de carga en camiones de tipo LIFO (Last-In, First-Out).
> El último paquete en entrar al camión es el primero en salir en la ruta de entrega.
> Los estudiantes deben optimizar la carga para que el camión no tenga que vaciarse en cada parada.

- El tope de la pila = primera entrega en la ruta
- Si se carga mal, el camión debe vaciarse en cada parada ❌
- Si se optimiza, el destino más cercano queda arriba ✅

```python
pila = Pila(capacidad=8)
pila.apilar(paquete)    # Carga al camión → va al tope
pkg  = pila.desapilar() # Primera entrega → sale del tope (LIFO)
```

---

### 📚 Donde Usar Arrays — `Array Bidimensional [6][5]`
> Inventario de estanterías fijas del almacén.
> El array representa las posiciones físicas de los pasillos donde se guardan productos según su categoría.

- Cada fila = una categoría (Normal, Frágil, Pesado, Express, Devolución, Refrigerado)
- Cada columna = un slot físico del pasillo (S1 a S5)
- Acceso directo por índice `[categoría][slot]` en tiempo O(1)

```python
# Array: 6 categorías × 5 slots = 30 posiciones físicas
estantes = ArrayEstantes(CATEGORIAS, slots=5)
estantes.guardar(paquete)      # Busca primer slot libre en su categoría
estantes.retirar(pkg_id)       # Libera la posición al entregar
```

---

### 🖥 Frontend GUI — `Tkinter`
> El desarrollo debe tener Frontend para que el usuario interactúe.

Interfaz gráfica completa construida con **Python Tkinter** — sin dependencias externas.

---

## 🏗 Arquitectura del Código

```
amazon_hub.py
│
├── class Cola              # Estructura FIFO (collections.deque)
│   ├── encolar()
│   ├── desencolar()
│   ├── frente()
│   └── esta_vacia() / tamaño()
│
├── class Pila              # Estructura LIFO (list)
│   ├── apilar()
│   ├── desapilar()
│   ├── tope()
│   └── esta_llena() / esta_vacia()
│
├── class ArrayEstantes     # Array 2D [categoría][slot]
│   ├── guardar()
│   ├── retirar()
│   └── obtener_todo() / total_ocupado()
│
├── class Paquete           # Modelo de datos
│   └── id, destino, tipo, hora
│
└── class AmazonHubApp      # GUI principal (hereda tk.Tk)
    ├── _build_header()
    ├── _build_queue_panel()     ← Visualiza la Cola
    ├── _build_shelf_visual()    ← Visualiza el Array
    ├── _build_truck_panel()     ← Visualiza la Pila
    ├── _build_inventory_panel() ← Inventario + Ruta óptima
    └── _build_log_panel()       ← Registro de operaciones
```

---

## 🎮 Guía de Uso

| Botón | Acción | Estructura |
|-------|--------|------------|
| `+ REGISTRAR` | Crea paquete → lo encola y guarda en estante | Cola + Array |
| `▶ Procesar Cola` | Extrae el primero de la cola (FIFO) | Cola |
| `🚛 Cargar Camión` | Mueve de la cola al camión (push a la pila) | Cola + Pila |
| `⬇ Descargar (LIFO)` | Retira el tope del camión (pop de la pila) | Pila |
| `🚀 Despachar` | Entrega todos en orden LIFO y genera ruta | Pila + Array |
| `⟳ Reset` | Reinicia todas las estructuras | Todas |

### Flujo recomendado para optimizar la ruta:
```
1. Registrar paquetes con diferentes destinos
2. Cargar al camión en orden INVERSO al de entrega
   (el destino más lejano sube primero → queda en el fondo)
   (el destino más cercano sube último → queda en el tope)
3. Despachar → el camión entrega sin vaciarse en cada parada ✅
```

---

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.7 o superior
- Tkinter (incluido por defecto en Python — no requiere `pip install`)

### Ejecutar
```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/amazon-hub.git
cd amazon-hub

# Ejecuta el simulador
python amazon_hub.py
```

> **Linux:** Si Tkinter no está instalado → `sudo apt install python3-tk`

---

## 📁 Estructura del Repositorio

```
amazon-hub/
├── amazon_hub.py       # Código fuente principal
└── README.md           # Este archivo
```

---

## 🛠 Tecnologías

| Tecnología | Uso |
|------------|-----|
| `Python 3.x` | Lenguaje principal |
| `tkinter` | Interfaz gráfica (GUI) |
| `ttk` | Widgets estilizados |
| `collections.deque` | Implementación de la Cola FIFO |
| `list` nativo | Implementación de la Pila LIFO |
| `datetime` | Timestamps en el registro de operaciones |

---

## 📐 Complejidad de Operaciones

| Operación | Estructura | Complejidad |
|-----------|------------|-------------|
| `encolar / desencolar` | Cola (deque) | O(1) |
| `apilar / desapilar` | Pila (list) | O(1) |
| `guardar / retirar` | Array estantes | O(n) búsqueda de slot libre |
| `acceso directo [i][j]` | Array estantes | O(1) |

---

## 👥 Caso de Estudio — Estructuras de Datos

Este proyecto fue desarrollado como caso de estudio para la materia de **Estructuras de Datos**, demostrando la aplicación práctica de:

- **Cola (Queue)** → problema de orden y equidad en atención
- **Pila (Stack)** → problema de optimización de carga y rutas
- **Array bidimensional** → problema de indexación y acceso a inventario físico

---

*Desarrollado con Python 🐍 y Tkinter*
