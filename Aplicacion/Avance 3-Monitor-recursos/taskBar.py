# taskBar.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from datetime import datetime


class TaskBar(ttk.Frame):
    """Barra inferior reutilizable con ícono, fecha y hora en tiempo real (alineadas simétricamente)."""

    def __init__(self, parent, controller):
        super().__init__(parent, style="Dark.TFrame")
        self.controller = controller
        self.configure(style="Dark.TFrame")

        base_path = os.path.join(os.path.dirname(__file__), "icons")
        path_icon_bar = os.path.join(base_path, "iconInsanOS.png")

        self.bar = tk.Canvas(self, height=45, bg="#2b2b2b", highlightthickness=0)
        self.bar.pack(fill="x", padx=20, pady=12)

        # Cargar íconos
        try:
            img = Image.open(path_icon_bar).resize((35, 35))
            img_big = Image.open(path_icon_bar).resize((45, 45))
            self.icon_bar = ImageTk.PhotoImage(img)
            self.icon_bar_big = ImageTk.PhotoImage(img_big)
        except Exception:
            self.icon_bar = None
            self.icon_bar_big = None

        self.bar.bind("<Configure>", self._draw_bar)

    def _draw_bar(self, event=None):
        """Dibuja la barra con bordes redondeados, ícono y fecha/hora."""
        bar = self.bar
        bar.delete("all")
        w = bar.winfo_width()
        h = bar.winfo_height()
        color = "#8c8c8c"
        r = 15

        # Fondo redondeado
        bar.create_oval(0, 0, 2*r, 2*r, fill=color, outline=color)
        bar.create_oval(w - 2*r, 0, w, 2*r, fill=color, outline=color)
        bar.create_oval(0, h - 2*r, 2*r, h, fill=color, outline=color)
        bar.create_oval(w - 2*r, h - 2*r, w, h, fill=color, outline=color)
        bar.create_rectangle(r, 0, w - r, h, fill=color, outline=color)
        bar.create_rectangle(0, r, w, h - r, fill=color, outline=color)

        # Ícono izquierdo (volver al escritorio)
        left_padding = 40
        if self.icon_bar:
            icon_id = bar.create_image(left_padding, h // 2, image=self.icon_bar)
            bar.tag_bind(icon_id, "<Button-1>", lambda e: self.controller.show_view("desktop"))

            # Animación hover
            def enlarge(_):
                bar.itemconfig(icon_id, image=self.icon_bar_big)
                bar.config(cursor="hand2")

            def restore(_):
                bar.itemconfig(icon_id, image=self.icon_bar)
                bar.config(cursor="arrow")

            bar.tag_bind(icon_id, "<Enter>", enlarge)
            bar.tag_bind(icon_id, "<Leave>", restore)

        # --- Fecha y hora actualizadas dinámicamente ---
        def update_datetime():
            now = datetime.now()
            current_date = now.strftime("%d/%m/%Y")
            current_time = now.strftime("%H:%M")
            display_text = f"{current_date} | {current_time}"

            bar.delete("datetime_text")
            # Mismo padding que el ícono (40 px del borde derecho)
            bar.create_text(
                w - left_padding, h // 2,
                text=display_text,
                fill="white",
                font=("Segoe UI", 10, "bold"),
                tags="datetime_text",
                anchor="e"
            )

            bar.after(60000, update_datetime)

        update_datetime()
