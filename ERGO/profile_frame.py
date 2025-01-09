import tkinter as tk

class ProfileFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        tk.Label(self, text="You clicked Profile", font=("Arial", 24), bg="white").pack(expand=True)
