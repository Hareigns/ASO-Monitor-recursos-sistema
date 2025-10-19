import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from taskBar import TaskBar


class DesktopView(ttk.Frame):
    """Vista principal tipo escritorio de InsanOS."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="Dark.TFrame")
        self._build_ui()

    def _build_ui(self):
        base_path = os.path.join(os.path.dirname(__file__), "icons")
        path_wallpaper = os.path.join(base_path, "logoInsanOS.png")
        path_info = os.path.join(base_path, "info.png")
        path_monitor = os.path.join(base_path, "monitorApp.png")

        # Fondo escritorio
        bg = tk.Canvas(self, bg="#2b2b2b", highlightthickness=0)
        bg.pack(fill="both", expand=True)

        # --- LOGO centrado en la mitad derecha ---
        try:
            img_wallpaper = Image.open(path_wallpaper).resize((923, 655), Image.LANCZOS)
            self.wallpaper = ImageTk.PhotoImage(img_wallpaper)

            def position_logo(event=None):
                bg.delete("logo")
                w, h = bg.winfo_width(), bg.winfo_height()
                x_pos = w * 0.65   # 75% del ancho → mitad derecha
                y_pos = h * 0.5    # centro vertical
                bg.create_image(x_pos, y_pos, image=self.wallpaper, anchor="center", tags="logo")

            bg.bind("<Configure>", position_logo)
        except Exception:
            self.wallpaper = None

        # ---- Panel lateral superior (iconos verticales) ----
        side_panel = tk.Frame(self, bg="#2b2b2b", highlightthickness=0)
        side_panel.place(x=20, y=30)  # padding izquierdo igual al taskbar y subidos un poco

        # Íconos
        icon_size = (35, 35)
        icon_hover = (45, 45)

        def load_icon(path, size):
            try:
                return ImageTk.PhotoImage(Image.open(path).resize(size))
            except Exception:
                return None

        self.icon_info = load_icon(path_info, icon_size)
        self.icon_info_big = load_icon(path_info, icon_hover)
        self.icon_monitor = load_icon(path_monitor, icon_size)
        self.icon_monitor_big = load_icon(path_monitor, icon_hover)

        self.lbl_pres = tk.Label(side_panel, image=self.icon_info, bg="#2b2b2b", cursor="hand2")
        self.lbl_pres.pack(pady=(0, 8))
        tk.Label(side_panel, text="Presentación", bg="#2b2b2b", fg="white").pack(pady=(0, 15))

        self.lbl_monitor = tk.Label(side_panel, image=self.icon_monitor, bg="#2b2b2b", cursor="hand2")
        self.lbl_monitor.pack(pady=(0, 8))
        tk.Label(side_panel, text="Monitor", bg="#2b2b2b", fg="white").pack()

        # Hover
        self.lbl_pres.bind("<Enter>", lambda e: self.lbl_pres.config(image=self.icon_info_big))
        self.lbl_pres.bind("<Leave>", lambda e: self.lbl_pres.config(image=self.icon_info))
        self.lbl_monitor.bind("<Enter>", lambda e: self.lbl_monitor.config(image=self.icon_monitor_big))
        self.lbl_monitor.bind("<Leave>", lambda e: self.lbl_monitor.config(image=self.icon_monitor))

        # Clic
        self.lbl_pres.bind("<Button-1>", lambda e: self.controller.show_view("presentation"))
        self.lbl_monitor.bind("<Button-1>", lambda e: self.controller.show_view("monitor"))

        # ---- Barra inferior reutilizable ----
        taskbar = TaskBar(self, self.controller)
        taskbar.pack(side="bottom", fill="x")
