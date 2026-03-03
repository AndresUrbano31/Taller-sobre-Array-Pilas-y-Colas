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

CATEGORIAS = ["Normal", "Frágil", "Pesado", "Express", "Devolución", "Refrigerado"]
SLOTS_POR_CATEGORIA = 5
CAPACIDAD_CAMION = 8

# ──────────────────────────────────────────────────────────────
#  ESTRUCTURAS DE DATOS
# ──────────────────────────────────────────────────────────────

class Cola:
    """Cola FIFO — recepción de pedidos en orden de llegada."""
    def __init__(self):
        self._datos = deque()

    def encolar(self, paquete):
        self._datos.append(paquete)

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("Cola vacía")
        return self._datos.popleft()

    def frente(self):
        return self._datos[0] if self._datos else None

    def esta_vacia(self):
        return len(self._datos) == 0

    def tamaño(self):
        return len(self._datos)

    def elementos(self):
        return list(self._datos)


class Pila:
    """Pila LIFO — carga del camión: último en entrar, primero en salir."""
    def __init__(self, capacidad=CAPACIDAD_CAMION):
        self._datos = []
        self.capacidad = capacidad

    def apilar(self, paquete):
        if self.esta_llena():
            raise OverflowError("Pila llena (camión al máximo)")
        self._datos.append(paquete)

    def desapilar(self):
        if self.esta_vacia():
            raise IndexError("Pila vacía")
        return self._datos.pop()

    def tope(self):
        return self._datos[-1] if self._datos else None

    def esta_vacia(self):
        return len(self._datos) == 0

    def esta_llena(self):
        return len(self._datos) >= self.capacidad

    def tamaño(self):
        return len(self._datos)

    def elementos(self):
        return list(self._datos)


class ArrayEstantes:
    """
    Array bidimensional [categoría][slot] — inventario de posiciones
    físicas fijas en los pasillos del almacén.
    """
    def __init__(self, categorias, slots):
        self.categorias = categorias
        self.slots = slots
        # Array: None = libre, Paquete = ocupado
        self._datos = [[None] * slots for _ in range(len(categorias))]

    def guardar(self, paquete):
        cat_idx = self.categorias.index(paquete.tipo) if paquete.tipo in self.categorias else 0
        for slot in range(self.slots):
            if self._datos[cat_idx][slot] is None:
                self._datos[cat_idx][slot] = paquete
                return cat_idx, slot
        return None, None  # sin espacio en esa categoría

    def retirar(self, pkg_id):
        for cat in range(len(self.categorias)):
            for slot in range(self.slots):
                p = self._datos[cat][slot]
                if p and p.id == pkg_id:
                    self._datos[cat][slot] = None
                    return cat, slot
        return None, None

    def obtener_todo(self):
        return [row[:] for row in self._datos]

    def total_ocupado(self):
        return sum(1 for row in self._datos for cell in row if cell)


# ──────────────────────────────────────────────────────────────
#  MODELO
# ──────────────────────────────────────────────────────────────

class Paquete:
    _contador = 1

    def __init__(self, pkg_id, destino, tipo):
        self.id = pkg_id or f"PKG-{Paquete._contador:03d}"
        Paquete._contador += 1
        self.destino = destino
        self.tipo = tipo
        self.hora = datetime.now().strftime("%H:%M:%S")

    def __repr__(self):
        return f"Paquete({self.id}, {self.destino}, {self.tipo})"


# ──────────────────────────────────────────────────────────────
#  APLICACIÓN TKINTER
# ──────────────────────────────────────────────────────────────

class AmazonHubApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Amazon Hub — Simulador de Logística y Rutas")
        self.configure(bg=C["bg"])
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.resizable(True, True)

        # Estructuras
        self.cola    = Cola()
        self.pila    = Pila(CAPACIDAD_CAMION)
        self.estantes = ArrayEstantes(CATEGORIAS, SLOTS_POR_CATEGORIA)
        self.entregados = 0
        self.total_reg  = 0

        # Estilo ttk
        self._configurar_estilos()

        # Layout
        self._build_header()
        self._build_body()

        # Demo inicial
        self._cargar_demo()

    # ── ESTILOS ──────────────────────────────────────────────

    def _configurar_estilos(self):
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
        self.lbl_h_cola      = self._hstat(stats_f, "EN COLA")
        self.lbl_h_camion    = self._hstat(stats_f, "CAMIÓN")
        self.lbl_h_entregado = self._hstat(stats_f, "ENTREGADOS")

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

        # Columna izquierda — Cola
        self._build_queue_panel(body)

        # Centro
        self._build_center(body)

        # Columna derecha — Inventario
        self._build_inventory_panel(body)

    # ── PANEL COLA ───────────────────────────────────────────

    def _build_queue_panel(self, parent):
        frame = self._card(parent, side="left", width=280, fill="y")

        # Título
        self._panel_title(frame, "📥  COLA DE RECEPCIÓN",
                          "Estructura: Queue (FIFO)", C["cyan"])

        # Hint
        self._hint(frame, "⚡ FIFO: primero en llegar = primero en procesar")

        # Lista
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

        # Stats pequeñas
        sg = tk.Frame(frame, bg=C["surface"], pady=6)
        sg.pack(fill="x", padx=8, pady=(0, 8))
        g = tk.Frame(sg, bg=C["surface"])
        g.pack(fill="x")
        self.stat_cola     = self._mini_stat(g, "0", "EN COLA",    C["cyan"])
        self.stat_entregad = self._mini_stat(g, "0", "ENTREGADOS", C["green"])
        self.stat_cam_stat = self._mini_stat(g, "0", "EN CAMIÓN",  C["purple"])
        self.stat_estante  = self._mini_stat(g, "0", "ESTANTES",   C["amazon"])

    # ── CENTRO ───────────────────────────────────────────────

    def _build_center(self, parent):
        center = tk.Frame(parent, bg=C["bg"])
        center.pack(side="left", fill="both", expand=True)

        self._build_input_section(center)

        # Área principal dividida: estantes arriba, camión abajo
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
        self._btn(row1, "+ REGISTRAR", self.registrar_paquete,
                  C["amazon"], "#000", side="left")

        # Row 2 — acciones
        row2 = tk.Frame(inp, bg=C["surface"])
        row2.pack(fill="x")

        self._btn(row2, "▶ Procesar Cola",    self.procesar_cola,    C["cyan"],    "#000")
        self._btn(row2, "🚛 Cargar Camión",   self.cargar_camion,    C["purple"],  "#fff")
        self._btn(row2, "⬇ Descargar (LIFO)", self.descargar_camion, C["yellow"],  "#000")
        self._btn(row2, "🚀 Despachar",        self.despachar_camion, C["green"],   "#000")
        self._btn(row2, "⟳ Reset",             self.reset_todo,       C["red"],     "#fff")

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

        # Encabezados de slots
        tk.Label(grid_f, text="CATEGORÍA", bg=C["surface"],
                 fg=C["text_dim"], font=("Consolas", 7), width=12,
                 anchor="w").grid(row=0, column=0, padx=2, pady=2)
        for s in range(SLOTS_POR_CATEGORIA):
            tk.Label(grid_f, text=f"SLOT {s+1}", bg=C["surface"],
                     fg=C["text_dim"], font=("Consolas", 7),
                     width=11).grid(row=0, column=s+1, padx=2)

        self.shelf_cells = []
        for r, cat in enumerate(CATEGORIAS):
            tk.Label(grid_f, text=cat, bg=C["surface"],
                     fg=C["text_dim"], font=("Consolas", 8),
                     width=12, anchor="w").grid(row=r+1, column=0, padx=2, pady=2)
            row_cells = []
            for s in range(SLOTS_POR_CATEGORIA):
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

        # Área de la pila — muestra de arriba (tope) hacia abajo
        self.truck_frame = tk.Frame(frame, bg=C["surface2"],
                                    relief="flat", bd=1)
        self.truck_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.truck_rows = []
        for i in range(CAPACIDAD_CAMION):
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
        tk.Button(hdr, text="LIMPIAR", command=self._limpiar_log,
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

    # ── PANEL INVENTARIO ─────────────────────────────────────

    def _build_inventory_panel(self, parent):
        frame = self._card(parent, side="right", width=280, fill="y")

        self._panel_title(frame, "🗂  INVENTARIO",
                          "Estructura: Array[cat][slot]", C["amazon"])
        self._hint(frame, "📐 Posiciones físicas fijas por categoría y slot")

        # Lista scrolleable
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

        # Ruta óptima
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

    # ── OPERACIONES PRINCIPALES ───────────────────────────────

    def registrar_paquete(self):
        pkg_id = self.pkg_id_var.get().strip().upper()
        destino = self.pkg_dest_var.get().strip()
        tipo = self.pkg_type_var.get()

        if not destino:
            messagebox.showwarning("Campo requerido", "Ingresa el destino del paquete.")
            return

        if not pkg_id:
            pkg_id = f"PKG-{self.total_reg + 1:03d}"

        pkg = Paquete(pkg_id, destino, tipo)
        self.total_reg += 1

        # → Cola FIFO
        self.cola.encolar(pkg)

        # → Array estantes
        cat_idx, slot = self.estantes.guardar(pkg)
        if cat_idx is not None:
            cat_nombre = CATEGORIAS[cat_idx]
            self.log(f"📥 Cola.encolar({pkg.id}) → destino: {pkg.destino} | tipo: {pkg.tipo}", "info")
            self.log(f"📐 Array.guardar() → Estante {cat_nombre}-S{slot+1}", "warn")
        else:
            self.log(f"📥 Cola.encolar({pkg.id}) → estantes de {tipo} llenos", "warn")

        # Limpiar inputs
        self.pkg_id_var.set("")
        self.pkg_dest_var.set("")

        self._actualizar_todo()

    def procesar_cola(self):
        if self.cola.esta_vacia():
            self.log("⚠ Cola vacía — no hay paquetes que procesar", "error")
            return
        pkg = self.cola.desencolar()
        self.log(f"▶ Cola.desencolar() → {pkg.id} procesado (FIFO: primero en llegar)", "success")
        self.log(f"   Paquete {pkg.id} listo para cargar al camión", "info")
        self._actualizar_todo()

    def cargar_camion(self):
        if self.cola.esta_vacia():
            self.log("⚠ No hay paquetes en cola para cargar al camión", "error")
            return
        if self.pila.esta_llena():
            self.log("⚠ Pila.apilar() → OVERFLOW: camión lleno (8/8)", "error")
            return
        pkg = self.cola.desencolar()
        self.pila.apilar(pkg)
        self.log(f"🚛 Pila.apilar({pkg.id}) → camión [{self.pila.tamaño()}/{self.pila.capacidad}] | LIFO activo", "purple")
        self._actualizar_todo()

    def descargar_camion(self):
        if self.pila.esta_vacia():
            self.log("⚠ Pila vacía — camión sin carga", "error")
            return
        pkg = self.pila.desapilar()
        self.log(f"⬇ Pila.desapilar() → {pkg.id} descargado (LIFO: último en entrar, primero en salir)", "purple")
        self._actualizar_todo()

    def despachar_camion(self):
        if self.pila.esta_vacia():
            self.log("⚠ Camión vacío — carga paquetes primero", "error")
            return
        cantidad = self.pila.tamaño()
        self.log(f"🚀 DESPACHO — Camión con {cantidad} paquetes en ruta LIFO", "success")

        # Desapilar en orden LIFO y entregar
        orden = 1
        while not self.pila.esta_vacia():
            pkg = self.pila.desapilar()
            self.entregados += 1
            self.estantes.retirar(pkg.id)
            self.log(f"   📍 Parada {orden}: {pkg.id} entregado en {pkg.destino}", "success")
            orden += 1

        self.log(f"✅ Camión regresó — {cantidad} paquetes entregados", "success")
        self._actualizar_todo()

    def reset_todo(self):
        if not messagebox.askyesno("Confirmar Reset",
                                   "¿Reiniciar todo el sistema?"):
            return
        self.cola      = Cola()
        self.pila      = Pila(CAPACIDAD_CAMION)
        self.estantes  = ArrayEstantes(CATEGORIAS, SLOTS_POR_CATEGORIA)
        self.entregados = 0
        self.total_reg  = 0
        Paquete._contador = 1
        self.log("⟳ Sistema reiniciado completamente", "warn")
        self._actualizar_todo()

    # ── ACTUALIZACIONES UI ────────────────────────────────────

    def _actualizar_todo(self):
        self._actualizar_cola_panel()
        self._actualizar_camion()
        self._actualizar_estantes()
        self._actualizar_inventario()
        self._actualizar_ruta()
        self._actualizar_header()

    def _actualizar_header(self):
        en_estante = self.estantes.total_ocupado()
        self.lbl_h_total.config(     text=str(self.total_reg))
        self.lbl_h_cola.config(      text=str(self.cola.tamaño()))
        self.lbl_h_camion.config(    text=str(self.pila.tamaño()))
        self.lbl_h_entregado.config( text=str(self.entregados))
        self.stat_cola.config(     text=str(self.cola.tamaño()))
        self.stat_entregad.config( text=str(self.entregados))
        self.stat_cam_stat.config( text=str(self.pila.tamaño()))
        self.stat_estante.config(  text=str(en_estante))

    def _actualizar_cola_panel(self):
        for w in self.queue_inner.winfo_children():
            w.destroy()

        items = self.cola.elementos()
        if not items:
            tk.Label(self.queue_inner, text="📭  Cola vacía\nRegistra un paquete",
                     bg=C["surface"], fg=C["text_dim"],
                     font=("Consolas", 9), justify="center",
                     pady=20).pack(fill="x", padx=8)
            return

        for i, pkg in enumerate(items):
            color = TYPE_COLOR.get(pkg.tipo, C["cyan"])
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

            tk.Label(info, text=f"{TYPE_EMOJI.get(pkg.tipo,'')} {pkg.id}",
                     bg=bg, fg=color,
                     font=("Consolas", 9, "bold")).pack(anchor="w")
            tk.Label(info, text=f"▸ {pkg.destino}",
                     bg=bg, fg=C["text_dim"],
                     font=("Consolas", 7)).pack(anchor="w")

            tk.Label(row, text=pkg.tipo.upper(),
                     bg=bg, fg=color,
                     font=("Consolas", 7),
                     padx=4).pack(side="right", padx=4)

    def _actualizar_camion(self):
        # Mostrar pila de abajo a arriba visualmente (tope arriba)
        elems = list(reversed(self.pila.elementos()))
        self.lbl_camion_cap.config(
            text=f"{self.pila.tamaño()} / {self.pila.capacidad} paquetes")

        for i, row_lbl in enumerate(self.truck_rows):
            if i < len(elems):
                pkg = elems[i]
                color = TYPE_COLOR.get(pkg.tipo, C["purple"])
                es_tope = (i == 0)
                sufijo = "  ← SALE PRIMERO" if es_tope else ""
                row_lbl.config(
                    text=f"  {TYPE_EMOJI.get(pkg.tipo,'')} {pkg.id:10s} {pkg.destino:18s}{sufijo}",
                    bg=C["surface2"] if not es_tope else "#2d1f42",
                    fg=C["text"] if es_tope else C["purple"],
                    font=("Consolas", 9, "bold" if es_tope else "normal"))
            else:
                row_lbl.config(text="", bg=C["surface2"], fg=C["surface2"])

    def _actualizar_estantes(self):
        datos = self.estantes.obtener_todo()
        for r, row_cells in enumerate(self.shelf_cells):
            for s, cell in enumerate(row_cells):
                pkg = datos[r][s]
                if pkg:
                    color = TYPE_COLOR.get(pkg.tipo, C["amazon"])
                    cell.config(text=f"{pkg.id[:8]:^11}",
                                bg="#1c2a1c", fg=color,
                                relief="ridge")
                else:
                    cat = CATEGORIAS[r]
                    cell.config(text=f"[{cat[:3].upper()}-S{s+1}]",
                                bg=C["surface2"], fg=C["border"],
                                relief="flat")

    def _actualizar_inventario(self):
        for w in self.inv_inner.winfo_children():
            w.destroy()

        datos = self.estantes.obtener_todo()
        total = 0

        for r, cat in enumerate(CATEGORIAS):
            items = [(datos[r][s], s) for s in range(SLOTS_POR_CATEGORIA)
                     if datos[r][s] is not None]

            # Cabecera de categoría
            cat_hdr = tk.Frame(self.inv_inner, bg=C["surface2"])
            cat_hdr.pack(fill="x", padx=4, pady=(4, 1))
            color = TYPE_COLOR.get(cat, C["amazon"])
            tk.Label(cat_hdr, text=f"📁 {cat}",
                     bg=C["surface2"], fg=color,
                     font=("Consolas", 8, "bold"),
                     padx=6, pady=2).pack(side="left")
            tk.Label(cat_hdr, text=f"{len(items)}/{SLOTS_POR_CATEGORIA}",
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
                             text=f" {TYPE_EMOJI.get(pkg.tipo,'')} {pkg.id}",
                             bg=C["surface"], fg=C["text"],
                             font=("Consolas", 8)).pack(side="left")
                    tk.Label(row,
                             text=f"S{slot+1} · {pkg.destino[:12]}",
                             bg=C["surface"], fg=C["text_dim"],
                             font=("Consolas", 7)).pack(side="right", padx=4)
                    total += 1

        if total == 0:
            tk.Label(self.inv_inner,
                     text="Sin items en inventario",
                     bg=C["surface"], fg=C["text_dim"],
                     font=("Consolas", 8), pady=10).pack()

    def _actualizar_ruta(self):
        for w in self.route_frame.winfo_children():
            w.destroy()

        elems = list(reversed(self.pila.elementos()))  # tope primero
        if not elems:
            tk.Label(self.route_frame,
                     text="Carga el camión para ver la ruta",
                     bg=C["surface"], fg=C["text_dim"],
                     font=("Consolas", 8)).pack(anchor="w")
            return

        for i, pkg in enumerate(elems):
            color = TYPE_COLOR.get(pkg.tipo, C["purple"])
            row = tk.Frame(self.route_frame, bg=C["surface"])
            row.pack(fill="x", pady=1)

            num_lbl = tk.Label(row, text=f"{i+1}",
                               bg=C["purple"], fg="#000",
                               font=("Consolas", 7, "bold"),
                               width=2)
            num_lbl.pack(side="left", padx=(0, 6))

            info = tk.Frame(row, bg=C["surface"])
            info.pack(side="left", fill="x")
            tk.Label(info, text=pkg.destino,
                     bg=C["surface"], fg=C["text"],
                     font=("Consolas", 8)).pack(anchor="w")
            tk.Label(info, text=f"{TYPE_EMOJI.get(pkg.tipo,'')} {pkg.id} · {pkg.tipo}",
                     bg=C["surface"], fg=color,
                     font=("Consolas", 7)).pack(anchor="w")

    # ── LOG ───────────────────────────────────────────────────

    def log(self, msg, tag="info"):
        hora = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("1.0", f"{msg}\n", tag)
        self.log_text.insert("1.0", f"[{hora}] ", "time")
        self.log_text.config(state="disabled")

    def _limpiar_log(self):
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

    # ── DEMO ─────────────────────────────────────────────────

    def _cargar_demo(self):
        demos = [
            ("PKG-001", "Zona Norte",     "Express"),
            ("PKG-002", "Zona Sur",       "Frágil"),
            ("PKG-003", "Zona Este",      "Normal"),
            ("PKG-004", "Centro Urbano",  "Pesado"),
        ]
        for pid, dest, tipo in demos:
            self.pkg_id_var.set(pid)
            self.pkg_dest_var.set(dest)
            self.pkg_type_var.set(tipo)
            self.registrar_paquete()

        self.log("🏭 Sistema Amazon Hub iniciado — demo cargado con 4 paquetes", "success")
        self._actualizar_todo()


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AmazonHubApp()
    app.mainloop()
