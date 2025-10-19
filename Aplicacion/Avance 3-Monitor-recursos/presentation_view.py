import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from taskBar import TaskBar


class PresentationView(ttk.Frame):
    """Vista institucional de presentación del proyecto (responsive)."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(style="Main.TFrame")

        # Colores institucionales
        self.fondo_general = "#cfcfcf"
        self.cuadro_central = "#3a3a3a"
        self.texto_azul = "#1b76d2"
        self.texto_blanco = "#ffffff"

        # Canvas principal
        self.bg = tk.Canvas(self, bg=self.fondo_general, highlightthickness=0)
        self.bg.pack(fill="both", expand=True)

        # Imagen del logo
        try:
            self.logo_img = Image.open("icons/uniLogo.png")
        except Exception:
            self.logo_img = None

        # Vincular evento de redimensionamiento
        self.bg.bind("<Configure>", self._redraw)

        # Barra inferior
        self.taskbar = TaskBar(self, self.controller)
        self.taskbar.pack(side="bottom", fill="x")

    def _redraw(self, event):
        """Redibuja el contenido del Canvas proporcionalmente."""
        self.bg.delete("all")

        w, h = event.width, event.height
        ref_w, ref_h = 1280, 720
        scale_x = w / ref_w
        scale_y = h / ref_h
        scale = min(scale_x, scale_y)

        # Centrar el contenido en el Canvas
        offset_x = (w - ref_w * scale) / 2
        offset_y = (h - ref_h * scale) / 2

        def sx(x): return offset_x + x * scale
        def sy(y): return offset_y + y * scale

        # --- Cuadro central redondeado ---
        self._rounded_rectangle(sx(20), sy(40), sx(1260), sy(650), r=40*scale, fill=self.cuadro_central)

        # --- Logos ---
        if self.logo_img:
            logo_scaled = self.logo_img.resize((int(105*scale), int(80*scale)))
            logo_tk = ImageTk.PhotoImage(logo_scaled)
            self.bg.create_image(sx(180), sy(130), image=logo_tk, anchor="center")
            self.bg.create_image(sx(1100), sy(130), image=logo_tk, anchor="center")
            self.bg.image = logo_tk  # mantener referencia

        # --- Textos institucionales ---
        self._text(sx(640), sy(150), "UNIVERSIDAD NACIONAL DE INGENIERÍA", 18*scale, "bold", self.texto_azul)
        self._text(sx(640), sy(180), "ÁREA DE CONOCIMIENTO DE TECNOLOGÍA DE LA INFORMACIÓN Y COMUNICACIÓN", 11*scale, "", self.texto_azul)
        self._text(sx(640), sy(205), "ARQUITECTURA DE SISTEMAS OPERATIVOS", 11*scale, "bold", self.texto_azul)
        self._text(sx(640), sy(235), "TRABAJO DE CURSO : SIMULACIÓN DEL MONITOR DE RECURSOS DEL SISTEMA", 11*scale, "", self.texto_blanco)

        # --- Bloque de integrantes y docente ---
        y_title, y_name, y_code = 295, 325, 345

        self._text(sx(60), sy(y_title), "Elaborado por:", 11*scale, "bold", self.texto_azul, "w")
        self._text(sx(945), sy(y_title), "Docente:", 11*scale, "bold", self.texto_azul, "w")

        integrantes = [
            ("José Antonio Martín Zelaya", "2021-0056U"),
            ("Harvin Gabriel Gutiérrez Guillén", "2021-0127U"),
            ("Kevin Geovanni Cerpas González", "2020-0441U"),
        ]

        start_x, spacing = 60, 280
        for i, (nombre, codigo) in enumerate(integrantes):
            x = start_x + (i * spacing)
            self._text(sx(x), sy(y_name), nombre, 11*scale, "", self.texto_blanco, "w")
            self._text(sx(x), sy(y_code), codigo, 11*scale, "", self.texto_blanco, "w")

        self._text(sx(945), sy(y_name), "Jacqueline Janette Montes López", 11*scale, "", self.texto_blanco, "w")

        for x in [315, 610, 920]:
            self.bg.create_line(sx(x), sy(305), sx(x), sy(395), fill=self.texto_azul, width=2*scale)

        # --- Grupo y fecha ---
        self._text(sx(140), sy(430), "Grupo: 4T3-COM-S", 11*scale, "bold", self.texto_azul, "center")
        self._text(sx(160), sy(500), "22 de octubre del 2025\nManagua, Nicaragua", 11*scale, "", self.texto_azul, "center")

    # --- Función de texto auxiliar ---
    def _text(self, x, y, text, size, weight, color, anchor="center"):
        font = ("Orbitron", max(6, int(size)), weight)
        self.bg.create_text(x, y, text=text, font=font, fill=color, anchor=anchor)

    # --- Función de rectángulo redondeado ---
    def _rounded_rectangle(self, x1, y1, x2, y2, r=30, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return self.bg.create_polygon(points, smooth=True, **kwargs)
