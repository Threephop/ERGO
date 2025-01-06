import tkinter as tk

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")
        tk.Label(self, text="Home Page", bg="#ffffff", fg="#000000", font=("Arial", 24)).pack(expand=True)
