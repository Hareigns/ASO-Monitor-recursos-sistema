import os
import ttkbootstrap as tb
from ttkbootstrap import Style
import tkinter as tk
from desktop_view import DesktopView
from presentation_view import PresentationView
from monitor_view import MonitorView


class App(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Monitor del Sistema - InsanOS Prototype")
        self.geometry("1280x720")
        self.resizable(True, True)

        # Use Orbitron family name for font (must be installed system-wide)
        orbitron_font = ("Orbitron", 12)

        # Neon style for ttkbootstrap
        style = Style()
        style.configure("Neon.TFrame", background="#181825")
        style.configure("Neon.TLabel", background="#181825", foreground="#00fff7", font=orbitron_font)
        style.configure("Neon.TButton", background="#181825", foreground="#ff00ea", font=orbitron_font)
        # Neon Progressbar style
        style.configure("Neon.Horizontal.TProgressbar", troughcolor="#23243a", background="#00fff7", bordercolor="#181825", lightcolor="#00fff7", darkcolor="#181825")
        # Neon Treeview style
        style.configure("Neon.Treeview", background="#23243a", foreground="#00fff7", fieldbackground="#23243a", rowheight=28, font=("Orbitron", 13))
        style.map("Neon.Treeview", background=[("selected", "#181825")], foreground=[("selected", "#ff00ea")])

        # Contenedor principal
        container = tb.Frame(self, style="Neon.TFrame")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Vistas registradas
        self.views = {}
        for V in (DesktopView, PresentationView, MonitorView):
            frame = V(container, self)
            name = V.__name__.replace("View", "").lower()
            self.views[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Mostrar vista inicial
        self.show_view("desktop")

    def show_view(self, name: str):
        """Muestra una vista por nombre."""
        frame = self.views.get(name)
        if frame:
            frame.tkraise()
        else:
            tk.messagebox.showerror("Error", f"No se encontró la vista: {name}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
