# monitor_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import psutil
import os
import threading
from collections import deque
import time
from taskBar import TaskBar  # ✅ importamos la barra reutilizable

UPDATE_INTERVAL_MS = 500  # intervalo de actualización


class MonitorView(ttk.Frame):
    """Vista del Monitor de Recursos del Sistema (revisada y corregida)."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="Neon.TFrame")

        # datos de red para calcular delta
        try:
            self.last_net = psutil.net_io_counters()
        except Exception:
            self.last_net = None

        # historial para graficar CPU
        self.cpu_history = deque(maxlen=60)

        # Primer pase de inicialización de cpu_percent de procesos
        threading.Thread(target=self._prime_process_cpu, daemon=True).start()

        # Construir la interfaz
        self._build()

        # Iniciar loop de actualización
        self.after(500, self.update_metrics)

    def _prime_process_cpu(self):
        """Inicializa las métricas de CPU por proceso."""
        try:
            for p in psutil.process_iter():
                try:
                    p.cpu_percent(None)
                except Exception:
                    pass
            time.sleep(0.2)
        except Exception:
            pass

    def _build(self):
        # --- Header ---
        header = tk.Frame(self, bg="#181825")
        header.pack(fill="x", pady=(8, 6))
        tk.Label(header, text="Monitor de Recursos", font=("Consolas", 24, "bold"), fg="#00fff7", bg="#181825").pack(side="left", padx=12)
        

        # --- Área principal ---
        main_area = tk.Frame(self, bg="#181825")
        main_area.pack(fill="both", expand=True, padx=12, pady=(6, 6))

        # panel izquierdo (neon dark)
        self.left_panel = tk.Frame(main_area, bg="#23243a", width=380, highlightbackground="#00fff7", highlightthickness=3)
        self.left_panel.pack(side="left", fill="y", padx=(0, 18), pady=8)

        # panel derecho (gráficos / procesos)
        self.right_panel = tk.Frame(main_area, bg="#181825")
        self.right_panel.pack(side="left", fill="both", expand=True, pady=8)

        # ---- Contenido del panel izquierdo ----
        tk.Label(self.left_panel, text="Resumen del Sistema", bg="#23243a", fg="#00fff7", font=("Consolas", 18, "bold"), borderwidth=0, highlightthickness=0).pack(anchor="w", padx=16, pady=(12, 16))

        # CPU
        tk.Label(self.left_panel, text="CPU", bg="#23243a", fg="#00fff7", font=("Consolas", 14, "bold"), borderwidth=0, highlightthickness=0).pack(anchor="w", padx=16)
        self.cpu_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=280, mode="determinate", maximum=100, style="Neon.Horizontal.TProgressbar")
        self.cpu_bar.pack(anchor="w", padx=16, pady=(6, 2))
        self.cpu_label = tk.Label(self.left_panel, text="0%", bg="#23243a", fg="#00fff7", font=("Consolas", 13), borderwidth=0, highlightthickness=0)
        self.cpu_label.pack(anchor="w", padx=16, pady=(0, 14))

        # Memoria
        tk.Label(self.left_panel, text="Memoria", bg="#23243a", fg="#ff00ea", font=("Consolas", 14, "bold"), borderwidth=0, highlightthickness=0).pack(anchor="w", padx=16)
        self.mem_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=280, mode="determinate", maximum=100, style="Neon.Horizontal.TProgressbar")
        self.mem_bar.pack(anchor="w", padx=16, pady=(6, 2))
        self.mem_label = tk.Label(self.left_panel, text="0%", bg="#23243a", fg="#ff00ea", font=("Consolas", 13), borderwidth=0, highlightthickness=0)
        self.mem_label.pack(anchor="w", padx=16, pady=(0, 14))

        # Disco
        tk.Label(self.left_panel, text="Disco (root)", bg="#23243a", fg="#00ff7f", font=("Consolas", 14, "bold"), borderwidth=0, highlightthickness=0).pack(anchor="w", padx=16)
        self.disk_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=280, mode="determinate", maximum=100, style="Neon.Horizontal.TProgressbar")
        self.disk_bar.pack(anchor="w", padx=16, pady=(6, 2))
        self.disk_label = tk.Label(self.left_panel, text="0%", bg="#23243a", fg="#00ff7f", font=("Consolas", 13), borderwidth=0, highlightthickness=0)
        self.disk_label.pack(anchor="w", padx=16, pady=(0, 14))

        # Red
        tk.Label(self.left_panel, text="Red (total)", bg="#23243a", fg="#ffef6e", font=("Consolas", 14, "bold"), borderwidth=0, highlightthickness=0).pack(anchor="w", padx=16)
        self.net_label = tk.Label(self.left_panel, text="Enviar: 0 KB/s | Recibir: 0 KB/s", bg="#23243a", fg="#ffef6e", font=("Consolas", 13), borderwidth=0, highlightthickness=0)
        self.net_label.pack(anchor="w", padx=16, pady=(6, 18))

        # ---- Panel derecho ----
        hist_frame = tk.LabelFrame(self.right_panel, text="Histórico CPU (últ. ~60 muestras)", font=("Consolas", 14), fg="#00fff7", bg="#181825", bd=3, labelanchor="n")
        hist_frame.pack(fill="x", padx=8, pady=(0, 10))
        self.canvas = tk.Canvas(hist_frame, height=120, bg="#23243a", highlightthickness=0)
        self.canvas.pack(fill="x", padx=8, pady=8)

        # Procesos
        proc_frame = tk.LabelFrame(self.right_panel, text="Procesos (ordenados por CPU%)", font=("Consolas", 14), fg="#ff00ea", bg="#181825", bd=3, labelanchor="n")
        proc_frame.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        cols = ("pid", "name", "cpu%", "mem%")
        self.proc_tree = ttk.Treeview(proc_frame, columns=cols, show="headings", style="Neon.Treeview")
        for c in cols:
            self.proc_tree.heading(c, text=c.upper())
            if c == "name":
                self.proc_tree.column(c, width=300, anchor="w")
            else:
                self.proc_tree.column(c, width=80, anchor="center")
        self.proc_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(proc_frame, orient="vertical", command=self.proc_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.proc_tree.configure(yscrollcommand=scrollbar.set)

        # ---- Barra inferior reutilizable ----
        taskbar = TaskBar(self, self.controller)
        taskbar.pack(side="bottom", fill="x")

    # --- Métodos auxiliares ---
    def _draw_cpu_history(self):
        """Dibuja el historial de CPU en el canvas."""
        self.canvas.delete("all")
        w = max(10, self.canvas.winfo_width())
        h = max(10, self.canvas.winfo_height())
        hist = list(self.cpu_history)
        if not hist:
            return
        step = w / max(1, (len(hist) - 1))
        lastx, lasty = 0, h - (hist[0] / 100.0) * h
        for i, v in enumerate(hist):
            x = i * step
            y = h - (v / 100.0) * h
            if i > 0:
                self.canvas.create_line(lastx, lasty, x, y, width=2, fill="#1f77b4")
            lastx, lasty = x, y
        for p in (25, 50, 75):
            y = h - (p / 100.0) * h
            self.canvas.create_line(0, y, w, y, dash=(2, 4))

    def update_metrics(self):
        """Recoger métricas y actualizar UI periódicamente."""
        try:
            cpu = psutil.cpu_percent(interval=None)
            self.cpu_history.append(cpu)
            self.cpu_bar['value'] = cpu
            self.cpu_label.config(text=f"{cpu:.1f}%")

            mem = psutil.virtual_memory()
            mem_pct = mem.percent
            self.mem_bar['value'] = mem_pct
            self.mem_label.config(text=f"{mem_pct:.1f}% de {round(mem.total / (1024**3), 2)} GB")

            try:
                disk = psutil.disk_usage('/')
                disk_pct = disk.percent
                self.disk_bar['value'] = disk_pct
                self.disk_label.config(text=f"{disk_pct:.1f}% de {round(disk.total / (1024**3), 2)} GB")
            except Exception:
                self.disk_bar['value'] = 0
                self.disk_label.config(text="No disponible")

            try:
                cur_net = psutil.net_io_counters()
                if self.last_net:
                    sent_delta = (cur_net.bytes_sent - self.last_net.bytes_sent) / 1024.0
                    recv_delta = (cur_net.bytes_recv - self.last_net.bytes_recv) / 1024.0
                else:
                    sent_delta = recv_delta = 0.0
                self.last_net = cur_net
                self.net_label.config(text=f"Enviar: {sent_delta:.1f} KB/s  |  Recibir: {recv_delta:.1f} KB/s")
            except Exception:
                self.net_label.config(text="Red: no disponible")

            self._draw_cpu_history()

            procs = []
            try:
                for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    info = p.info
                    procs.append((info['pid'], info['name'] or "", info.get('cpu_percent') or 0.0, info.get('memory_percent') or 0.0))
                procs.sort(key=lambda x: x[2], reverse=True)
                top = procs[:100]
            except Exception:
                top = []

            self.proc_tree.delete(*self.proc_tree.get_children())
            for pid, name, cpu_p, mem_p in top:
                self.proc_tree.insert("", "end", values=(pid, name[:35], f"{cpu_p:.1f}", f"{mem_p:.1f}"))
        except Exception:
            pass

        self.after(UPDATE_INTERVAL_MS, self.update_metrics)
