"""
╔══════════════════════════════════════════════════════════════╗
║         AMAZON HUB — Simulador de Logística y Rutas         ║
║  Estructuras: Cola (FIFO) · Pila (LIFO) · Array (Estantes)  ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import deque
import random

# ──────────────────────────────────────────────────────────────
#  PALETA DE COLORES  (tema oscuro estilo industrial)
# ──────────────────────────────────────────────────────────────
C = {
    "bg":        "#0d1117",
    "surface":   "#161b22",
    "surface2":  "#21262d",
    "border":    "#30363d",
    "amazon":    "#ff9900",
    "cyan":      "#39c5cf",
    "green":     "#3fb950",
    "red":       "#f85149",
    "purple":    "#a371f7",
    "yellow":    "#e3b341",
    "text":      "#e6edf3",
    "text_dim":  "#7d8590",
}

TYPE_COLOR = {
    "Normal":   C["cyan"],
    "Frágil":   C["red"],
    "Pesado":   C["purple"],
    "Express":  C["amazon"],
}

TYPE_EMOJI = {
    "Normal":  "📦",
    "Frágil":  "🔴",
    "Pesado":  "🟣",
    "Express": "🟠",
}

CATEGORIES = ["Normal", "Frágil", "Pesado", "Express", "Devolución", "Refrigerado"]
SLOTS_PER_CATEGORY = 5
TRUCK_CAPACITY = 8

# ──────────────────────────────────────────────────────────────
#  DATA STRUCTURES
# ──────────────────────────────────────────────────────────────

class Queue:
    """FIFO Queue — reception of orders in arrival order."""
    def __init__(self):
        self._data = deque()

    def enqueue(self, package):
        self._data.append(package)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Cola vacía")
        return self._data.popleft()

    def front(self):
        return self._data[0] if self._data else None

    def is_empty(self):
        return len(self._data) == 0

    def size(self):
        return len(self._data)

    def elements(self):
        return list(self._data)


class Stack:
    """LIFO Stack — truck loading: last in, first out."""
    def __init__(self, capacity=TRUCK_CAPACITY):
        self._data = []
        self.capacity = capacity

    def push(self, package):
        if self.is_full():
            raise OverflowError("Pila llena (camión al máximo)")
        self._data.append(package)

    def pop(self):
        if self.is_empty():
            raise IndexError("Pila vacía")
        return self._data.pop()

    def peek(self):
        return self._data[-1] if self._data else None

    def is_empty(self):
        return len(self._data) == 0

    def is_full(self):
        return len(self._data) >= self.capacity

    def size(self):
        return len(self._data)

    def elements(self):
        return list(self._data)


class ShelfArray:
    """
    2D Array [category][slot] — inventory of fixed physical positions
    in the warehouse aisles.
    """
    def __init__(self, categories, slots):
        self.categories = categories
        self.slots = slots
        # Array: None = free, Package = occupied
        self._data = [[None] * slots for _ in range(len(categories))]

    def store(self, package):
        cat_idx = self.categories.index(package.type) if package.type in self.categories else 0
        for slot in range(self.slots):
            if self._data[cat_idx][slot] is None:
                self._data[cat_idx][slot] = package
                return cat_idx, slot
        return None, None  # no space in that category

    def remove(self, pkg_id):
        for cat in range(len(self.categories)):
            for slot in range(self.slots):
                p = self._data[cat][slot]
                if p and p.id == pkg_id:
                    self._data[cat][slot] = None
                    return cat, slot
        return None, None

    def get_all(self):
        return [row[:] for row in self._data]

    def total_occupied(self):
        return sum(1 for row in self._data for cell in row if cell)


# ──────────────────────────────────────────────────────────────
#  MODEL
# ──────────────────────────────────────────────────────────────

class Package:
    _counter = 1

    def __init__(self, pkg_id, destination, pkg_type):
        self.id = pkg_id or f"PKG-{Package._counter:03d}"
        Package._counter += 1
        self.destination = destination
        self.type = pkg_type
        self.time = datetime.now().strftime("%H:%M:%S")

    def __repr__(self):
        return f"Package({self.id}, {self.destination}, {self.type})"


# ──────────────────────────────────────────────────────────────
#  TKINTER APPLICATION
# ──────────────────────────────────────────────────────────────

class AmazonHubApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Amazon Hub — Simulador de Logística y Rutas")
        self.configure(bg=C["bg"])
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.resizable(True, True)

        # Structures
        self.queue    = Queue()
        self.stack    = Stack(TRUCK_CAPACITY)
        self.shelves  = ShelfArray(CATEGORIES, SLOTS_PER_CATEGORY)
        self.delivered_count = 0
        self.total_registered  = 0

        # TTK Style
        self._configure_styles()

        # Layout
        self._build_header()
        self._build_body()

        # Initial Demo
        self._load_demo()

    # ── STYLES ──────────────────────────────────────────────

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame",       background=C["bg"])
        style.configure("Card.TFrame",  background=C["surface"],  relief="flat")
        style.configure("Inner.TFrame", background=C["surface2"], relief="flat")
        style.configure("TLabel",       background=C["bg"],       foreground=C["text"],
                        font=("Consolas", 9))
        style.configure("Title.TLabel", background=C["surface"],  foreground=C["amazon"],
                        font=("Consolas", 11, "bold"))
        style.configure("Sub.TLabel",   background=C["surface"],  foreground=C["text_dim"],
                        font=("Consolas", 8))
        style.configure("Stat.TLabel",  background=C["surface2"], foreground=C["text"],
                        font=("Consolas", 9))
        style.configure("TEntry",       fieldbackground=C["surface2"], foreground=C["text"],
                        insertcolor=C["text"], borderwidth=1, relief="flat",
                        font=("Consolas", 9))
        style.configure("TCombobox",    fieldbackground=C["surface2"], foreground=C["text"],
                        background=C["surface2"], selectbackground=C["surface2"],
                        font=("Consolas", 9))
        style.map("TCombobox",
                  fieldbackground=[("readonly", C["surface2"])],
                  selectbackground=[("readonly", C["surface2"])],
                  foreground=[("readonly", C["text"])])

        # Scrollbar
        style.configure("Vertical.TScrollbar",
                        background=C["border"], troughcolor=C["surface"],
                        borderwidth=0, arrowsize=12)

    # ── HEADER ───────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg="#0a0d12", height=56)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Logo
        logo_f = tk.Frame(hdr, bg="#0a0d12")
        logo_f.pack(side="left", padx=16)
        tk.Label(logo_f, text="📦", bg=C["amazon"], font=("", 18),
                 width=2).pack(side="left", pady=8)
        tk.Label(logo_f, text="  AMAZON HUB", bg="#0a0d12",
                 fg=C["text"], font=("Consolas", 14, "bold")).pack(side="left")
        tk.Label(logo_f, text=" — Simulador de Logística", bg="#0a0d12",
                 fg=C["text_dim"], font=("Consolas", 9)).pack(side="left")

        # Stats
        stats_f = tk.Frame(hdr, bg="#0a0d12")
        stats_f.pack(side="right", padx=16)

        self.lbl_h_total     = self._hstat(stats_f, "TOTAL")
        self.lbl_h_queue     = self._hstat(stats_f, "EN COLA")
        self.lbl_h_truck     = self._hstat(stats_f, "CAMIÓN")
        self.lbl_h_delivered = self._hstat(stats_f, "ENTREGADOS")

        # Status
        status_f = tk.Frame(hdr, bg="#0a0d12")
        status_f.pack(side="right", padx=16)
        tk.Label(status_f, text="● SISTEMA OPERATIVO", bg="#0a0d12",
                 fg=C["green"], font=("Consolas", 9)).pack()

    def _hstat(self, parent, label):
        f = tk.Frame(parent, bg="#0a0d12", padx=12)
        f.pack(side="left")
        lbl_val = tk.Label(f, text="0", bg="#0a0d12",
                           fg=C["amazon"], font=("Consolas", 14, "bold"))
        lbl_val.pack()
        tk.Label(f, text=label, bg="#0a0d12",
                 fg=C["text_dim"], font=("Consolas", 7)).pack()
        return lbl_val

    # ── BODY ─────────────────────────────────────────────────

    def _build_body(self):
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left Column — Queue
        self._build_queue_panel(body)

        # Center
        self._build_center(body)

        # Right Column — Inventory
        self._build_inventory_panel(body)

    # ── QUEUE PANEL ───────────────────────────────────────────

    def _build_queue_panel(self, parent):
        frame = self._card(parent, side="left", width=280, fill="y")

        # Title
        self._panel_title(frame, "📥  COLA DE RECEPCIÓN",
                          "Estructura: Queue (FIFO)", C["cyan"])

        # Hint
        self._hint(frame, "⚡ FIFO: primero en llegar = primero en procesar")

        # List
        list_frame = tk.Frame(frame, bg=C["surface"])
        list_frame.pack(fill="both", expand=True, padx=8)

        self.queue_canvas = tk.Canvas(list_frame, bg=C["surface"],
                                      highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(list_frame, orient="vertical",
                           command=self.queue_canvas.yview)
        self.queue_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.queue_canvas.pack(side="left", fill="both", expand=True)

        self.queue_inner = tk.Frame(self.queue_canvas, bg=C["surface"])
        self.queue_canvas.create_window((0, 0), window=self.queue_inner,
                                        anchor="nw")
        self.queue_inner.bind("<Configure>",
            lambda e: self.queue_canvas.configure(
                scrollregion=self.queue_canvas.bbox("all")))

        # Small Stats
        sg = tk.Frame(frame, bg=C["surface"], pady=6)
        sg.pack(fill="x", padx=8, pady=(0, 8))
        g = tk.Frame(sg, bg=C["surface"])
        g.pack(fill="x")
        self.stat_queue     = self._mini_stat(g, "0", "EN COLA",    C["cyan"])
        self.stat_delivered = self._mini_stat(g, "0", "ENTREGADOS", C["green"])
        self.stat_truck_load = self._mini_stat(g, "0", "EN CAMIÓN",  C["purple"])
        self.stat_shelf     = self._mini_stat(g, "0", "ESTANTES",   C["amazon"])

    # ── CENTER ───────────────────────────────────────────────

    def _build_center(self, parent):
        center = tk.Frame(parent, bg=C["bg"])
        center.pack(side="left", fill="both", expand=True)

        self._build_input_section(center)

        # Main area split: shelves top, truck bottom
        main_area = tk.Frame(center, bg=C["bg"])
        main_area.pack(fill="both", expand=True)

        self._build_shelf_visual(main_area)
        self._build_truck_panel(main_area)
        self._build_log_panel(center)

    def _build_input_section(self, parent):
        inp = tk.Frame(parent, bg=C["surface"], pady=10, padx=12)
        inp.pack(fill="x")

        # Row 1 — inputs
        row1 = tk.Frame(inp, bg=C["surface"])
        row1.pack(fill="x", pady=(0, 8))

        self._field(row1, "ID Paquete", "pkg_id", width=10)
        tk.Frame(row1, bg=C["surface"], width=8).pack(side="left")
        self._field(row1, "Destino", "pkg_dest", width=16)
        tk.Frame(row1, bg=C["surface"], width=8).pack(side="left")
        self._combo(row1, "Tipo", "pkg_type",
                    ["Normal", "Frágil", "Pesado", "Express"])

        tk.Frame(row1, bg=C["surface"], width=12).pack(side="left")
        self._btn(row1, "+ REGISTRAR", self.register_package,
                  C["amazon"], "#000", side="left")

        # Row 2 — actions
        row2 = tk.Frame(inp, bg=C["surface"])
        row2.pack(fill="x")

        self._btn(row2, "▶ Procesar Cola",    self.process_queue,    C["cyan"],    "#000")
        self._btn(row2, "🚛 Cargar Camión",   self.load_truck,    C["purple"],  "#fff")
        self._btn(row2, "⬇ Descargar (LIFO)", self.unload_truck, C["yellow"],  "#000")
        self._btn(row2, "🚀 Despachar",        self.dispatch_truck, C["green"],   "#000")
        self._btn(row2, "⟳ Reset",             self.reset_all,       C["red"],     "#fff")

    def _build_shelf_visual(self, parent):
        frame = self._card(parent, side="top", fill="x", pady_inner=8)

        tk.Label(frame, text="📚  ESTANTERÍAS DEL ALMACÉN — Array[categoría][slot]",
                 bg=C["surface"], fg=C["amazon"],
                 font=("Consolas", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 4))
        tk.Label(frame,
                 text="Cada celda representa una posición física fija. Verde = ocupado.",
                 bg=C["surface"], fg=C["text_dim"],
                 font=("Consolas", 8)).pack(anchor="w", padx=10, pady=(0, 6))

        grid_f = tk.Frame(frame, bg=C["surface"])
        grid_f.pack(fill="x", padx=10, pady=(0, 8))

        # Slot Headers
        tk.Label(grid_f, text="CATEGORÍA", bg=C["surface"],
                 fg=C["text_dim"], font=("Consolas", 7), width=12,
                 anchor="w").grid(row=0, column=0, padx=2, pady=2)
        for s in range(SLOTS_PER_CATEGORY):
            tk.Label(grid_f, text=f"SLOT {s+1}", bg=C["surface"],
                     fg=C["text_dim"], font=("Consolas", 7),
                     width=11).grid(row=0, column=s+1, padx=2)

        self.shelf_cells = []
        for r, cat in enumerate(CATEGORIES):
            tk.Label(grid_f, text=cat, bg=C["surface"],
                     fg=C["text_dim"], font=("Consolas", 8),
                     width=12, anchor="w").grid(row=r+1, column=0, padx=2, pady=2)
            row_cells = []
            for s in range(SLOTS_PER_CATEGORY):
                cell = tk.Label(grid_f, text=f"[  {cat[:3].upper()}-S{s+1}  ]",
                                bg=C["surface2"], fg=C["border"],
                                font=("Consolas", 7), width=11,
                                relief="flat", bd=1,
                                padx=2, pady=4)
                cell.grid(row=r+1, column=s+1, padx=2, pady=2)
                row_cells.append(cell)
            self.shelf_cells.append(row_cells)

    def _build_truck_panel(self, parent):
        frame = self._card(parent, side="top", fill="x", pady_inner=8)

        hdr = tk.Frame(frame, bg=C["surface"])
        hdr.pack(fill="x", padx=10, pady=(8, 4))

        tk.Label(hdr, text="🚛  CAMIÓN DE REPARTO — Pila (LIFO)",
                 bg=C["surface"], fg=C["purple"],
                 font=("Consolas", 10, "bold")).pack(side="left")

        self.lbl_camion_cap = tk.Label(hdr,
                                       text="0 / 8 paquetes",
                                       bg=C["surface"], fg=C["text_dim"],
                                       font=("Consolas", 8))
        self.lbl_camion_cap.pack(side="right")

        self._hint(frame,
                   "⬆ ÚLTIMO EN ENTRAR = PRIMERO EN SALIR · "
                   "Optimiza que el destino más cercano quede en el tope")

        # Stack Area — display from top (peek) to bottom
        self.truck_frame = tk.Frame(frame, bg=C["surface2"],
                                    relief="flat", bd=1)
        self.truck_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.truck_rows = []
        for i in range(TRUCK_CAPACITY):
            row = tk.Label(self.truck_frame,
                           text="",
                           bg=C["surface2"],
                           fg=C["purple"],
                           font=("Consolas", 9),
                           anchor="w", padx=8, pady=4,
                           relief="flat")
            row.pack(fill="x", padx=4, pady=1)
            self.truck_rows.append(row)

    def _build_log_panel(self, parent):
        frame = tk.Frame(parent, bg=C["surface"], height=130)
        frame.pack(fill="x", side="bottom")
        frame.pack_propagate(False)

        hdr = tk.Frame(frame, bg=C["surface"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="⬛ REGISTRO DE OPERACIONES",
                 bg=C["surface"], fg=C["text_dim"],
                 font=("Consolas", 8)).pack(side="left", padx=10, pady=4)
        tk.Button(hdr, text="LIMPIAR", command=self._clear_log,
                  bg=C["surface"], fg=C["text_dim"], relief="flat",
                  font=("Consolas", 7), cursor="hand2",
                  activebackground=C["surface2"],
                  activeforeground=C["text"]).pack(side="right", padx=10)

        log_inner = tk.Frame(frame, bg=C["surface"])
        log_inner.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_inner, bg=C["surface"],
                                fg=C["text_dim"], font=("Consolas", 8),
                                relief="flat", bd=0, state="disabled",
                                wrap="word", height=6)
        sb = ttk.Scrollbar(log_inner, orient="vertical",
                           command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True, padx=6)

        # Tags de color
        self.log_text.tag_configure("info",    foreground=C["cyan"])
        self.log_text.tag_configure("success", foreground=C["green"])
        self.log_text.tag_configure("warn",    foreground=C["amazon"])
        self.log_text.tag_configure("error",   foreground=C["red"])
        self.log_text.tag_configure("purple",  foreground=C["purple"])
        self.log_text.tag_configure("time",    foreground=C["text_dim"])

    # ── INVENTORY PANEL ─────────────────────────────────────

    def _build_inventory_panel(self, parent):
        frame = self._card(parent, side="right", width=280, fill="y")

        self._panel_title(frame, "🗂  INVENTARIO",
                          "Estructura: Array[cat][slot]", C["amazon"])
        self._hint(frame, "📐 Posiciones físicas fijas por categoría y slot")

        # Scrollable List
        inv_frame = tk.Frame(frame, bg=C["surface"])
        inv_frame.pack(fill="both", expand=True, padx=8)

        self.inv_canvas = tk.Canvas(inv_frame, bg=C["surface"],
                                    highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(inv_frame, orient="vertical",
                           command=self.inv_canvas.yview)
        self.inv_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.inv_canvas.pack(side="left", fill="both", expand=True)

        self.inv_inner = tk.Frame(self.inv_canvas, bg=C["surface"])
        self.inv_canvas.create_window((0, 0), window=self.inv_inner, anchor="nw")
        self.inv_inner.bind("<Configure>",
            lambda e: self.inv_canvas.configure(
                scrollregion=self.inv_canvas.bbox("all")))

        # Optimal Route
        sep = tk.Frame(frame, bg=C["border"], height=1)
        sep.pack(fill="x", padx=8, pady=4)

        tk.Label(frame, text="🗺  RUTA ÓPTIMA (orden LIFO)",
                 bg=C["surface"], fg=C["purple"],
                 font=("Consolas", 9, "bold")).pack(anchor="w", padx=10, pady=(4, 2))

        self._hint(frame, "El tope de la pila = primera entrega")

        self.route_frame = tk.Frame(frame, bg=C["surface"])
        self.route_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.lbl_route_empty = tk.Label(self.route_frame,
                                        text="Carga el camión para ver la ruta",
                                        bg=C["surface"], fg=C["text_dim"],
                                        font=("Consolas", 8))
        self.lbl_route_empty.pack(anchor="w")

    # ── MAIN OPERATIONS ───────────────────────────────

    def register_package(self):
        pkg_id = self.pkg_id_var.get().strip().upper()
        destination = self.pkg_dest_var.get().strip()
        pkg_type = self.pkg_type_var.get()

        if not destination:
            messagebox.showwarning("Campo requerido", "Ingresa el destino del paquete.")
            return

        if not pkg_id:
            pkg_id = f"PKG-{self.total_registered + 1:03d}"

        pkg = Package(pkg_id, destination, pkg_type)
        self.total_registered += 1

        # → FIFO Queue
        self.queue.enqueue(pkg)

        # → Shelf Array
        cat_idx, slot = self.shelves.store(pkg)
        if cat_idx is not None:
            cat_name = CATEGORIES[cat_idx]
            self.log(f"📥 Queue.enqueue({pkg.id}) → destino: {pkg.destination} | tipo: {pkg.type}", "info")
            self.log(f"📐 Array.store() → Estante {cat_name}-S{slot+1}", "warn")
        else:
            self.log(f"📥 Queue.enqueue({pkg.id}) → estantes de {pkg_type} llenos", "warn")

        # Clear inputs
        self.pkg_id_var.set("")
        self.pkg_dest_var.set("")

        self._update_all()

    def process_queue(self):
        if self.queue.is_empty():
            self.log("⚠ Cola vacía — no hay paquetes que procesar", "error")
            return
        pkg = self.queue.dequeue()
        self.log(f"▶ Queue.dequeue() → {pkg.id} procesado (FIFO: primero en llegar)", "success")
        self.log(f"   Paquete {pkg.id} listo para cargar al camión", "info")
        self._update_all()

    def load_truck(self):
        if self.queue.is_empty():
            self.log("⚠ No hay paquetes en cola para cargar al camión", "error")
            return
        if self.stack.is_full():
            self.log("⚠ Stack.push() → OVERFLOW: camión lleno (8/8)", "error")
            return
        pkg = self.queue.dequeue()
        self.stack.push(pkg)
        self.log(f"🚛 Stack.push({pkg.id}) → camión [{self.stack.size()}/{self.stack.capacity}] | LIFO activo", "purple")
        self._update_all()

    def unload_truck(self):
        if self.stack.is_empty():
            self.log("⚠ Pila vacía — camión sin carga", "error")
            return
        pkg = self.stack.pop()
        self.log(f"⬇ Stack.pop() → {pkg.id} descargado (LIFO: último en entrar, primero en salir)", "purple")
        self._update_all()

    def dispatch_truck(self):
        if self.stack.is_empty():
            self.log("⚠ Camión vacío — carga paquetes primero", "error")
            return
        count = self.stack.size()
        self.log(f"🚀 DESPACHO — Camión con {count} paquetes en ruta LIFO", "success")

        # Pop in LIFO order and deliver
        order = 1
        while not self.stack.is_empty():
            pkg = self.stack.pop()
            self.delivered_count += 1
            self.shelves.remove(pkg.id)
            self.log(f"   📍 Parada {order}: {pkg.id} entregado en {pkg.destination}", "success")
            order += 1

        self.log(f"✅ Camión regresó — {count} paquetes entregados", "success")
        self._update_all()

    def reset_all(self):
        if not messagebox.askyesno("Confirmar Reset",
                                   "¿Reiniciar todo el sistema?"):
            return
        self.queue      = Queue()
        self.stack      = Stack(TRUCK_CAPACITY)
        self.shelves  = ShelfArray(CATEGORIES, SLOTS_PER_CATEGORY)
        self.delivered_count = 0
        self.total_registered  = 0
        Package._counter = 1
        self.log("⟳ Sistema reiniciado completamente", "warn")
        self._update_all()

    # ── UI UPDATES ────────────────────────────────────

    def _update_all(self):
        self._update_queue_panel()
        self._update_truck_panel()
        self._update_shelves()
        self._update_inventory()
        self._update_route()
        self._update_header()

    def _update_header(self):
        on_shelf = self.shelves.total_occupied()
        self.lbl_h_total.config(     text=str(self.total_registered))
        self.lbl_h_queue.config(      text=str(self.queue.size()))
        self.lbl_h_truck.config(    text=str(self.stack.size()))
        self.lbl_h_delivered.config( text=str(self.delivered_count))
        self.stat_queue.config(     text=str(self.queue.size()))
        self.stat_delivered.config( text=str(self.delivered_count))
        self.stat_truck_load.config( text=str(self.stack.size()))
        self.stat_shelf.config(  text=str(on_shelf))

    def _update_queue_panel(self):
        for w in self.queue_inner.winfo_children():
            w.destroy()

        items = self.queue.elements()
        if not items:
            tk.Label(self.queue_inner, text="📭  Cola vacía\nRegistra un paquete",
                     bg=C["surface"], fg=C["text_dim"],
                     font=("Consolas", 9), justify="center",
                     pady=20).pack(fill="x", padx=8)
            return

        for i, pkg in enumerate(items):
            color = TYPE_COLOR.get(pkg.type, C["cyan"])
            bg = C["surface2"] if i > 0 else C["surface"]
            num_bg = color if i == 0 else C["border"]
            num_fg = "#000" if i == 0 else C["text_dim"]

            row = tk.Frame(self.queue_inner, bg=bg, pady=2)
            row.pack(fill="x", padx=4, pady=2)

            num = tk.Label(row, text=f"{i+1}", bg=num_bg, fg=num_fg,
                           font=("Consolas", 8, "bold"), width=2,
                           relief="flat")
            num.pack(side="left", padx=(4, 6), pady=2)

            info = tk.Frame(row, bg=bg)
            info.pack(side="left", fill="x", expand=True)

            tk.Label(info, text=f"{TYPE_EMOJI.get(pkg.type,'')} {pkg.id}",
                     bg=bg, fg=color,
                     font=("Consolas", 9, "bold")).pack(anchor="w")
            tk.Label(info, text=f"▸ {pkg.destination}",
                     bg=bg, fg=C["text_dim"],
                     font=("Consolas", 7)).pack(anchor="w")

            tk.Label(row, text=pkg.type.upper(),
                     bg=bg, fg=color,
                     font=("Consolas", 7),
                     padx=4).pack(side="right", padx=4)

    def _update_truck_panel(self):
        # Show stack from bottom to top visually (peek at top)
        elems = list(reversed(self.stack.elements()))
        self.lbl_camion_cap.config(
            text=f"{self.stack.size()} / {self.stack.capacity} paquetes")

        for i, row_lbl in enumerate(self.truck_rows):
            if i < len(elems):
                pkg = elems[i]
                color = TYPE_COLOR.get(pkg.type, C["purple"])
                es_tope = (i == 0)
                sufijo = "  ← SALE PRIMERO" if es_tope else ""
                row_lbl.config(
                    text=f"  {TYPE_EMOJI.get(pkg.type,'')} {pkg.id:10s} {pkg.destination:18s}{sufijo}",
                    bg=C["surface2"] if not es_tope else "#2d1f42",
                    fg=C["text"] if es_tope else C["purple"],
                    font=("Consolas", 9, "bold" if es_tope else "normal"))
            else:
                row_lbl.config(text="", bg=C["surface2"], fg=C["surface2"])

    def _update_shelves(self):
        data = self.shelves.get_all()
        for r, row_cells in enumerate(self.shelf_cells):
            for s, cell in enumerate(row_cells):
                pkg = data[r][s]
                if pkg:
                    color = TYPE_COLOR.get(pkg.type, C["amazon"])
                    cell.config(text=f"{pkg.id[:8]:^11}",
                                bg="#1c2a1c", fg=color,
                                relief="ridge")
                else:
                    cat = CATEGORIES[r]
                    cell.config(text=f"[{cat[:3].upper()}-S{s+1}]",
                                bg=C["surface2"], fg=C["border"],
                                relief="flat")

    def _update_inventory(self):
        for w in self.inv_inner.winfo_children():
            w.destroy()

        data = self.shelves.get_all()
        total = 0

        for r, cat in enumerate(CATEGORIES):
            items = [(data[r][s], s) for s in range(SLOTS_PER_CATEGORY)
                     if data[r][s] is not None]

            # Category Header
            cat_hdr = tk.Frame(self.inv_inner, bg=C["surface2"])
            cat_hdr.pack(fill="x", padx=4, pady=(4, 1))
            color = TYPE_COLOR.get(cat, C["amazon"])
            tk.Label(cat_hdr, text=f"📁 {cat}",
                     bg=C["surface2"], fg=color,
                     font=("Consolas", 8, "bold"),
                     padx=6, pady=2).pack(side="left")
            tk.Label(cat_hdr, text=f"{len(items)}/{SLOTS_PER_CATEGORY}",
                     bg=C["surface2"], fg=C["text_dim"],
                     font=("Consolas", 7)).pack(side="right", padx=6)

            if not items:
                tk.Label(self.inv_inner, text="  vacío",
                         bg=C["surface"], fg=C["border"],
                         font=("Consolas", 7)).pack(anchor="w", padx=8)
            else:
                for pkg, slot in items:
                    row = tk.Frame(self.inv_inner, bg=C["surface"])
                    row.pack(fill="x", padx=4, pady=1)
                    tk.Label(row, text="",
                             bg=color, width=2).pack(side="left")
                    tk.Label(row,
                             text=f" {TYPE_EMOJI.get(pkg.type,'')} {pkg.id}",
                             bg=C["surface"], fg=C["text"],
                             font=("Consolas", 8)).pack(side="left")
                    tk.Label(row,
                             text=f"S{slot+1} · {pkg.destination[:12]}",
                             bg=C["surface"], fg=C["text_dim"],
                             font=("Consolas", 7)).pack(side="right", padx=4)
                    total += 1

        if total == 0:
            tk.Label(self.inv_inner,
                     text="Sin items en inventario",
                     bg=C["surface"], fg=C["text_dim"],
                     font=("Consolas", 8), pady=10).pack()

    def _update_route(self):
        for w in self.route_frame.winfo_children():
            w.destroy()

        elems = list(reversed(self.stack.elements()))  # peek first
        if not elems:
            tk.Label(self.route_frame,
                     text="Carga el camión para ver la ruta",
                     bg=C["surface"], fg=C["text_dim"],
                     font=("Consolas", 8)).pack(anchor="w")
            return

        for i, pkg in enumerate(elems):
            color = TYPE_COLOR.get(pkg.type, C["purple"])
            row = tk.Frame(self.route_frame, bg=C["surface"])
            row.pack(fill="x", pady=1)

            num_lbl = tk.Label(row, text=f"{i+1}",
                               bg=C["purple"], fg="#000",
                               font=("Consolas", 7, "bold"),
                               width=2)
            num_lbl.pack(side="left", padx=(0, 6))

            info = tk.Frame(row, bg=C["surface"])
            info.pack(side="left", fill="x")
            tk.Label(info, text=pkg.destination,
                     bg=C["surface"], fg=C["text"],
                     font=("Consolas", 8)).pack(anchor="w")
            tk.Label(info, text=f"{TYPE_EMOJI.get(pkg.type,'')} {pkg.id} · {pkg.type}",
                     bg=C["surface"], fg=color,
                     font=("Consolas", 7)).pack(anchor="w")

    # ── LOG ───────────────────────────────────────────────────

    def log(self, msg, tag="info"):
        hora = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("1.0", f"{msg}\n", tag)
        self.log_text.insert("1.0", f"[{hora}] ", "time")
        self.log_text.config(state="disabled")

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    # ── HELPERS UI ────────────────────────────────────────────

    def _card(self, parent, side="left", width=None, fill="both",
              expand=False, pady_inner=0):
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        if width:
            outer.pack(side=side, fill=fill, padx=2, pady=2)
            outer.pack_propagate(False)
            outer.configure(width=width)
        else:
            outer.pack(side=side, fill=fill, expand=expand, padx=2, pady=2)
        inner = tk.Frame(outer, bg=C["surface"])
        inner.pack(fill="both", expand=True)
        return inner

    def _panel_title(self, parent, title, subtitle, color):
        hdr = tk.Frame(parent, bg=C["surface2"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg=C["surface2"], fg=color,
                 font=("Consolas", 10, "bold"),
                 padx=10, pady=6).pack(anchor="w")
        tk.Label(hdr, text=subtitle, bg=C["surface2"], fg=C["text_dim"],
                 font=("Consolas", 7), padx=10).pack(anchor="w")
        tk.Frame(hdr, bg=C["border"], height=1).pack(fill="x", pady=(4, 0))

    def _hint(self, parent, text):
        f = tk.Frame(parent, bg=C["surface"], padx=8, pady=2)
        f.pack(fill="x")
        bar = tk.Frame(f, bg=C["amazon"], width=3)
        bar.pack(side="left", fill="y")
        tk.Label(f, text=f"  {text}", bg=C["surface"], fg=C["text_dim"],
                 font=("Consolas", 7), wraplength=230, justify="left",
                 pady=4).pack(side="left")

    def _field(self, parent, label, var_name, width=12):
        f = tk.Frame(parent, bg=C["surface"])
        f.pack(side="left")
        tk.Label(f, text=label, bg=C["surface"], fg=C["text_dim"],
                 font=("Consolas", 7)).pack(anchor="w")
        var = tk.StringVar()
        setattr(self, f"{var_name}_var", var)
        entry = ttk.Entry(f, textvariable=var, width=width)
        entry.pack()

    def _combo(self, parent, label, var_name, options):
        f = tk.Frame(parent, bg=C["surface"])
        f.pack(side="left")
        tk.Label(f, text=label, bg=C["surface"], fg=C["text_dim"],
                 font=("Consolas", 7)).pack(anchor="w")
        var = tk.StringVar(value=options[0])
        setattr(self, f"{var_name}_var", var)
        cb = ttk.Combobox(f, textvariable=var, values=options,
                          state="readonly", width=10)
        cb.pack()

    def _btn(self, parent, text, command, bg, fg, side="left"):
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg, fg=fg,
                        font=("Consolas", 8, "bold"),
                        relief="flat", cursor="hand2",
                        padx=10, pady=5,
                        activebackground=bg,
                        activeforeground=fg)
        btn.pack(side=side, padx=4)

    def _mini_stat(self, parent, val, label, color):
        f = tk.Frame(parent, bg=C["surface2"], padx=8, pady=4)
        f.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        lbl_val = tk.Label(f, text=val, bg=C["surface2"],
                           fg=color, font=("Consolas", 14, "bold"))
        lbl_val.pack()
        tk.Label(f, text=label, bg=C["surface2"], fg=C["text_dim"],
                 font=("Consolas", 6)).pack()
        return lbl_val

    # ── DEMO ────────────────────────────────────────────────

    def _load_demo(self):
        demos = [
            ("PKG-001", "Zona Norte",     "Express"),
            ("PKG-002", "Zona Sur",       "Frágil"),
            ("PKG-003", "Zona Este",      "Normal"),
            ("PKG-004", "Centro Urbano",  "Pesado"),
        ]
        for pid, dest, pkg_type in demos:
            self.pkg_id_var.set(pid)
            self.pkg_dest_var.set(dest)
            self.pkg_type_var.set(pkg_type)
            self.register_package()

        self.log("🏭 Sistema Amazon Hub iniciado — demo cargado con 4 paquetes", "success")
        self._update_all()


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AmazonHubApp()
    app.mainloop()
